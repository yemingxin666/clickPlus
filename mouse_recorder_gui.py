#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鼠标动作录制器 - GUI 版本
基于 tkinter 的图形界面
"""

import json
import time
import threading
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path
from datetime import datetime
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Listener as KeyboardListener


# ============ Windows API 定义 ============

class MOUSEINPUT(ctypes.Structure):
    """Windows MOUSEINPUT 结构体"""
    _fields_ = [
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))
    ]


class INPUT(ctypes.Structure):
    """Windows INPUT 结构体（联合体简化版）"""
    _fields_ = [
        ('type', wintypes.DWORD),
        ('mi', MOUSEINPUT)
    ]


# Windows API 常量
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000


class MouseRecorderGUI:
    """鼠标录制器 GUI 版本"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎯 鼠标动作录制器 v2.0")
        self.root.geometry("800x650")
        self.root.resizable(True, True)

        # 录制器核心变量
        self.actions = []
        self.is_recording = False
        self.is_playing = False
        self.is_paused = False
        self.start_time = None
        self.mouse_controller = MouseController()
        self.mouse_listener = None
        self.last_move_time = 0
        self.move_threshold = 0.05
        self.playback_speed = 1.0
        self.loop_mode = False
        self.current_file = None
        self.smooth_move = True  # 平滑移动开关
        self.move_steps = 20  # 平滑移动的步数（增加到220步，更流畅）
        self.keyboard_listener = None  # 键盘监听器

        # 设置样式
        self.setup_styles()

        # 创建界面
        self.create_widgets()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 启动全局热键监听
        self.start_hotkey_listener()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 自定义按钮样式
        style.configure('Record.TButton', foreground='red', font=('Arial', 10, 'bold'))
        style.configure('Play.TButton', foreground='green', font=('Arial', 10, 'bold'))
        style.configure('Action.TButton', font=('Arial', 9))

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # === 标题区域 ===
        title_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        title_frame.columnconfigure(1, weight=1)

        # 录制控制按钮
        control_frame = ttk.Frame(title_frame)
        control_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        self.record_btn = ttk.Button(
            control_frame,
            text="🔴 开始录制",
            style='Record.TButton',
            command=self.toggle_recording,
            width=15
        )
        self.record_btn.pack(side=tk.LEFT, padx=5)

        self.play_btn = ttk.Button(
            control_frame,
            text="▶️ 播放",
            style='Play.TButton',
            command=self.toggle_playback,
            width=15
        )
        self.play_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            control_frame,
            text="⏹️ 停止",
            command=self.stop_playback,
            width=15,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # === 文件操作区域 ===
        file_frame = ttk.LabelFrame(main_frame, text="文件操作", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(
            file_frame,
            text="💾 保存录制",
            command=self.save_recording,
            style='Action.TButton',
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            file_frame,
            text="📂 加载录制",
            command=self.load_recording,
            style='Action.TButton',
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            file_frame,
            text="📊 统计信息",
            command=self.show_statistics,
            style='Action.TButton',
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # === 设置区域 ===
        settings_frame = ttk.LabelFrame(main_frame, text="播放设置", padding="10")
        settings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 循环模式
        self.loop_var = tk.BooleanVar(value=False)
        loop_check = ttk.Checkbutton(
            settings_frame,
            text="🔄 循环播放",
            variable=self.loop_var,
            command=self.toggle_loop
        )
        loop_check.pack(side=tk.LEFT, padx=10)

        # 平滑移动
        self.smooth_var = tk.BooleanVar(value=True)
        smooth_check = ttk.Checkbutton(
            settings_frame,
            text="🎬 平滑移动",
            variable=self.smooth_var,
            command=self.toggle_smooth
        )
        smooth_check.pack(side=tk.LEFT, padx=10)

        # 速度调节
        ttk.Label(settings_frame, text="⚡ 播放速度:").pack(side=tk.LEFT, padx=(20, 5))

        self.speed_var = tk.StringVar(value="1.0x")
        speed_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.speed_var,
            values=["0.5x", "1.0x", "1.5x", "2.0x", "3.0x"],
            width=8,
            state='readonly'
        )
        speed_combo.pack(side=tk.LEFT, padx=5)
        speed_combo.bind('<<ComboboxSelected>>', self.on_speed_change)

        # 采样阈值
        ttk.Label(settings_frame, text="🎯 采样间隔:").pack(side=tk.LEFT, padx=(20, 5))

        self.threshold_var = tk.StringVar(value="0.05")
        threshold_spin = ttk.Spinbox(
            settings_frame,
            from_=0.01,
            to=0.5,
            increment=0.01,
            textvariable=self.threshold_var,
            width=8,
            command=self.on_threshold_change
        )
        threshold_spin.pack(side=tk.LEFT, padx=5)

        ttk.Label(settings_frame, text="秒").pack(side=tk.LEFT)

        # === 状态栏 ===
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        # 日志输出
        log_label = ttk.Label(status_frame, text="📝 操作日志:", font=('Arial', 9, 'bold'))
        log_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(
            status_frame,
            height=15,
            width=80,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # === 底部信息栏 ===
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        info_frame.columnconfigure(1, weight=1)

        self.status_label = ttk.Label(
            info_frame,
            text="就绪",
            font=('Arial', 9),
            foreground='green'
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        # 热键提示
        hotkey_label = ttk.Label(
            info_frame,
            text="⌨️ F7-录制 F8-播放",
            font=('Arial', 9),
            foreground='gray'
        )
        hotkey_label.grid(row=0, column=1)

        self.action_count_label = ttk.Label(
            info_frame,
            text="动作数: 0",
            font=('Arial', 9)
        )
        self.action_count_label.grid(row=0, column=2, sticky=tk.E)

        # 初始化日志
        self.log("🎯 鼠标动作录制器 v2.0 已启动")
        self.log("📌 提示: 点击 [开始录制] 开始录制鼠标操作")

    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def update_status(self, message, color='black'):
        """更新状态栏"""
        self.status_label.config(text=message, foreground=color)

    def update_action_count(self):
        """更新动作计数"""
        self.action_count_label.config(text=f"动作数: {len(self.actions)}")

    # ============ 录制功能 ============

    def toggle_recording(self):
        """切换录制状态"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """开始录制"""
        if self.is_recording or self.is_playing:
            return

        self.actions = []
        self.is_recording = True
        self.start_time = time.time()
        self.last_move_time = 0

        self.record_btn.config(text="⏹️ 停止录制")
        self.play_btn.config(state='disabled')
        self.update_status("录制中...", 'red')
        self.log("🔴 开始录制鼠标动作...")

        # 启动鼠标监听器
        self.mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self.mouse_listener.start()

    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return

        self.is_recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None

        self.record_btn.config(text="🔴 开始录制")
        self.play_btn.config(state='normal')
        self.update_status("就绪", 'green')
        self.update_action_count()
        self.log(f"⏹️  录制停止，共录制 {len(self.actions)} 个动作")

    def _on_move(self, x, y):
        """鼠标移动事件"""
        if self.is_recording:
            current_time = time.time()
            timestamp = current_time - self.start_time

            if timestamp - self.last_move_time >= self.move_threshold:
                self.actions.append({
                    'type': 'move',
                    'x': x,
                    'y': y,
                    'time': timestamp
                })
                self.last_move_time = timestamp
                self.root.after(0, self.update_action_count)

    def _on_click(self, x, y, button, pressed):
        """鼠标点击事件"""
        if self.is_recording:
            timestamp = time.time() - self.start_time
            self.actions.append({
                'type': 'click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
                'time': timestamp
            })
            action_type = "按下" if pressed else "释放"
            self.root.after(0, lambda: self.log(f"🖱️  {button.name} {action_type} at ({x}, {y})"))

    def _on_scroll(self, x, y, dx, dy):
        """鼠标滚轮事件"""
        if self.is_recording:
            timestamp = time.time() - self.start_time
            self.actions.append({
                'type': 'scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'time': timestamp
            })
            self.root.after(0, lambda: self.log(f"🎡 滚轮滚动 at ({x}, {y}), dy={dy}"))

    # ============ 播放功能 ============

    def toggle_playback(self):
        """切换播放状态"""
        if not self.actions:
            messagebox.showwarning("警告", "没有录制的动作可以播放！")
            return

        if not self.is_playing:
            self.play_actions()
        else:
            self.pause_playback()

    def play_actions(self):
        """播放动作"""
        if not self.actions or self.is_recording:
            return

        if self.is_playing and self.is_paused:
            # 继续播放
            self.is_paused = False
            self.play_btn.config(text="⏸️ 暂停")
            self.update_status("播放中...", 'blue')
            self.log("▶️  继续播放...")
            return

        self.is_playing = True
        self.is_paused = False

        self.play_btn.config(text="⏸️ 暂停")
        self.stop_btn.config(state='normal')
        self.record_btn.config(state='disabled')
        self.update_status("播放中...", 'blue')
        self.log(f"▶️  开始播放，共 {len(self.actions)} 个动作...")

        # 在新线程中执行
        threading.Thread(target=self._execute_actions, daemon=True).start()

    def pause_playback(self):
        """暂停播放"""
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            self.play_btn.config(text="▶️ 继续")
            self.update_status("已暂停", 'orange')
            self.log("⏸️  播放已暂停")

    def stop_playback(self):
        """停止播放"""
        self.is_playing = False
        self.is_paused = False
        self.play_btn.config(text="▶️ 播放", state='normal')
        self.stop_btn.config(state='disabled')
        self.record_btn.config(state='normal')
        self.update_status("就绪", 'green')
        self.log("⏹️  播放已停止")

    def _execute_actions(self):
        """执行动作序列"""
        try:
            while True:
                prev_time = 0

                for action in self.actions:
                    if not self.is_playing:
                        return

                    # 处理暂停
                    while self.is_paused and self.is_playing:
                        time.sleep(0.1)

                    if not self.is_playing:
                        return

                    # 等待时间间隔
                    time_diff = action['time'] - prev_time
                    if time_diff > 0:
                        time.sleep(time_diff / self.playback_speed)
                    prev_time = action['time']

                    # 执行动作
                    try:
                        if action['type'] == 'move':
                            # 使用平滑移动，增加移动时间让轨迹更明显
                            move_duration = min(time_diff / self.playback_speed, 0.5)  # 最多0.5秒
                            self._smooth_move_to(action['x'], action['y'], move_duration)
                        elif action['type'] == 'click':
                            # 先平滑移动到点击位置，移动时间更长
                            self._smooth_move_to(action['x'], action['y'], 0.15)
                            button = self._parse_button(action['button'])
                            if action['pressed']:
                                self.mouse_controller.press(button)
                            else:
                                self.mouse_controller.release(button)
                        elif action['type'] == 'scroll':
                            # 先平滑移动到滚动位置
                            self._smooth_move_to(action['x'], action['y'], 0.15)
                            self.mouse_controller.scroll(action['dx'], action['dy'])
                    except Exception as e:
                        self.root.after(0, lambda e=e: self.log(f"⚠️  执行失败: {e}"))

                # 检查循环模式
                if not self.loop_mode:
                    break

                self.root.after(0, lambda: self.log("🔄 循环播放..."))

        finally:
            self.root.after(0, self._playback_finished)

    def _playback_finished(self):
        """播放完成"""
        self.is_playing = False
        self.is_paused = False
        self.play_btn.config(text="▶️ 播放", state='normal')
        self.stop_btn.config(state='disabled')
        self.record_btn.config(state='normal')
        self.update_status("就绪", 'green')
        self.log("✅ 播放完成")

    def _parse_button(self, button_str):
        """解析按钮"""
        if 'left' in button_str.lower():
            return Button.left
        elif 'right' in button_str.lower():
            return Button.right
        elif 'middle' in button_str.lower():
            return Button.middle
        return Button.left

    def _windows_move_mouse(self, x, y):
        """使用 Windows SendInput API 移动鼠标（确保光标可见）

        Args:
            x: 目标 X 坐标（屏幕绝对坐标）
            y: 目标 Y 坐标（屏幕绝对坐标）
        """
        # 获取屏幕尺寸
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)

        # 转换为 Windows 归一化坐标（0-65535）
        normalized_x = int(x * 65535 / screen_width)
        normalized_y = int(y * 65535 / screen_height)

        # 创建 MOUSEINPUT 结构
        mi = MOUSEINPUT(
            dx=normalized_x,
            dy=normalized_y,
            mouseData=0,
            dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
            time=0,
            dwExtraInfo=None
        )

        # 创建 INPUT 结构
        input_event = INPUT(type=INPUT_MOUSE, mi=mi)

        # 发送输入事件
        ctypes.windll.user32.SendInput(
            1,  # 事件数量
            ctypes.byref(input_event),  # 事件指针
            ctypes.sizeof(INPUT)  # 结构体大小
        )

    def _smooth_move_to(self, target_x, target_y, duration=0.1):
        """平滑移动鼠标到目标位置

        Args:
            target_x: 目标 X 坐标
            target_y: 目标 Y 坐标
            duration: 移动持续时间（秒）
        """
        if not self.smooth_move:
            # 如果关闭平滑移动，直接跳转（使用 SendInput API）
            self._windows_move_mouse(target_x, target_y)
            return

        # 获取当前位置
        current_x, current_y = self.mouse_controller.position

        # 计算距离
        distance_x = target_x - current_x
        distance_y = target_y - current_y

        # 如果距离很小，直接跳转（使用 SendInput API）
        if abs(distance_x) < 5 and abs(distance_y) < 5:
            self._windows_move_mouse(target_x, target_y)
            return

        # 计算移动步数和每步的延迟
        steps = self.move_steps
        # 确保每步至少有一定延迟，让移动清晰可见
        delay = max(duration / steps, 0.005)  # 至少5毫秒每步

        # 平滑移动（使用 SendInput API 确保光标可见）
        for i in range(1, steps + 1):
            if not self.is_playing:  # 检查是否停止播放
                break

            # 线性插值
            progress = i / steps
            current_pos_x = int(current_x + distance_x * progress)
            current_pos_y = int(current_y + distance_y * progress)

            self._windows_move_mouse(current_pos_x, current_pos_y)
            time.sleep(delay)

    # ============ 文件操作 ============

    def save_recording(self):
        """保存录制"""
        if not self.actions:
            messagebox.showwarning("警告", "没有可保存的录制！")
            return

        # 创建目录
        recordings_dir = Path("recordings")
        recordings_dir.mkdir(exist_ok=True)

        # 选择文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"recording_{timestamp}.json"

        filepath = filedialog.asksaveasfilename(
            initialdir=recordings_dir,
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )

        if not filepath:
            return

        try:
            data = {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'action_count': len(self.actions),
                'duration': self.actions[-1]['time'] if self.actions else 0,
                'actions': self.actions
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.current_file = Path(filepath)
            self.log(f"💾 录制已保存: {self.current_file.name}")
            self.log(f"   动作数: {len(self.actions)}, 时长: {data['duration']:.2f}秒")
            messagebox.showinfo("成功", f"录制已保存到:\n{filepath}")

        except Exception as e:
            self.log(f"❌ 保存失败: {e}")
            messagebox.showerror("错误", f"保存失败:\n{e}")

    def load_recording(self):
        """加载录制"""
        if self.is_recording or self.is_playing:
            messagebox.showwarning("警告", "请先停止录制或播放！")
            return

        filepath = filedialog.askopenfilename(
            initialdir="recordings",
            title="选择录制文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )

        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.actions = data.get('actions', [])
            self.current_file = Path(filepath)

            self.update_action_count()
            self.log(f"📂 录制已加载: {self.current_file.name}")
            self.log(f"   创建时间: {data.get('created_at', 'Unknown')}")
            self.log(f"   动作数: {len(self.actions)}, 时长: {data.get('duration', 0):.2f}秒")
            messagebox.showinfo("成功", f"录制已加载:\n{filepath}")

        except Exception as e:
            self.log(f"❌ 加载失败: {e}")
            messagebox.showerror("错误", f"加载失败:\n{e}")

    # ============ 设置功能 ============

    def toggle_loop(self):
        """切换循环模式"""
        self.loop_mode = self.loop_var.get()
        status = "开启" if self.loop_mode else "关闭"
        self.log(f"🔄 循环模式已{status}")

    def toggle_smooth(self):
        """切换平滑移动"""
        self.smooth_move = self.smooth_var.get()
        status = "开启" if self.smooth_move else "关闭"
        self.log(f"🎬 平滑移动已{status}")

    def on_speed_change(self, event=None):
        """速度改变"""
        speed_str = self.speed_var.get()
        self.playback_speed = float(speed_str.replace('x', ''))
        self.log(f"⚡ 播放速度: {speed_str}")

    def on_threshold_change(self):
        """采样阈值改变"""
        try:
            self.move_threshold = float(self.threshold_var.get())
            self.log(f"🎯 采样间隔: {self.move_threshold}秒")
        except ValueError:
            pass

    def show_statistics(self):
        """显示统计信息"""
        if not self.actions:
            messagebox.showinfo("统计信息", "没有录制数据")
            return

        move_count = sum(1 for a in self.actions if a['type'] == 'move')
        click_count = sum(1 for a in self.actions if a['type'] == 'click')
        scroll_count = sum(1 for a in self.actions if a['type'] == 'scroll')
        duration = self.actions[-1]['time'] if self.actions else 0

        stats = f"""
📊 录制统计信息

总动作数: {len(self.actions)}
移动事件: {move_count}
点击次数: {click_count // 2} 次 (共{click_count}个事件)
滚轮操作: {scroll_count}
录制时长: {duration:.2f} 秒

当前文件: {self.current_file.name if self.current_file else '未保存'}
循环模式: {'开启' if self.loop_mode else '关闭'}
平滑移动: {'开启' if self.smooth_move else '关闭'}
播放速度: {self.playback_speed}x
采样间隔: {self.move_threshold}秒
"""
        messagebox.showinfo("统计信息", stats)
        self.log("📊 已显示统计信息")

    def start_hotkey_listener(self):
        """启动全局热键监听"""
        self.keyboard_listener = KeyboardListener(on_press=self._on_hotkey_press)
        self.keyboard_listener.start()
        self.log("🎹 全局热键已启用: F7-录制 F8-播放")

    def _on_hotkey_press(self, key):
        """热键按下处理"""
        try:
            # F7: 开始/停止录制
            if key == Key.f7:
                self.root.after(0, self.toggle_recording)

            # F8: 开始/停止播放
            elif key == Key.f8:
                self.root.after(0, self.toggle_playback)

        except AttributeError:
            pass

    def toggle_recording(self):
        """切换录制状态（热键调用）"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def toggle_playback(self):
        """切换播放状态（热键调用）"""
        if not self.is_playing:
            if self.actions:
                self.play_actions()
            else:
                self.log("⚠️  没有录制数据，无法播放")
        else:
            self.stop_playback()

    def on_closing(self):
        """关闭窗口"""
        if self.is_recording:
            self.stop_recording()
        if self.is_playing:
            self.stop_playback()
        # 停止键盘监听
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = MouseRecorderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
