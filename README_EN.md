# 🎯 Mouse Action Recorder

[English](README_EN.md) | [中文](README.md)

A GUI-based mouse action recording and playback tool built with Python and tkinter. Record mouse movements, clicks, scrolls, and other operations with precise playback support.

## ✨ Features

- 🎥 **Recording Features**
  - Record mouse movement trajectories
  - Record mouse clicks (left, right, middle buttons)
  - Record scroll wheel operations
  - Adjustable sampling interval for recording precision

- ▶️ **Playback Features**
  - Precise playback of recorded mouse operations
  - Support pause/resume playback
  - Support loop playback mode
  - Adjustable playback speed (0.5x - 3.0x)
  - Smooth movement mode for natural mouse trajectories

- 💾 **File Management**
  - Save recordings in JSON format
  - Load previously saved recording files
  - Automatically create `recordings` directory for file storage

- ⌨️ **Shortcuts**
  - Global hotkey support
  - F7: Start/Stop recording
  - F8: Start/Stop playback

- 📊 **Statistics**
  - Display recording action count
  - Display recording duration
  - Statistics for various operation types

## 📋 System Requirements

- Windows operating system
- Python 3.6 or higher

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yemingxin666/clickPlus.git
cd clickPlus
```

### 2. Install Dependencies

#### Method 1: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Method 2: Direct Installation

```bash
pip install -r requirements.txt
```

### 3. Run the Program

#### Method 1: Using Batch File (Recommended)

Double-click `run_gui.bat` file, the program will automatically:
- Check virtual environment
- Launch the graphical interface

#### Method 2: Command Line

```bash
# If using virtual environment, activate it first
venv\Scripts\activate

# Run the program
python mouse_recorder_gui.py
```

## 📖 Usage Instructions

### Recording Operations

1. Click the **"🔴 Start Recording"** button or press **F7** key to start recording
2. Perform the mouse operations you want to record (movements, clicks, scrolls, etc.)
3. Click the **"⏹️ Stop Recording"** button or press **F7** again to stop recording

### Playback Operations

1. Ensure you have recorded data (obtained through recording or loading a file)
2. Click the **"▶️ Play"** button or press **F8** key to start playback
3. Click the **"⏸️ Pause"** button to pause playback
4. Click the **"⏹️ Stop"** button to stop playback

### Save and Load

- **Save Recording**: Click the **"💾 Save Recording"** button, choose save location, recording files will be saved in JSON format
- **Load Recording**: Click the **"📂 Load Recording"** button, select a previously saved JSON file

### Playback Settings

- **🔄 Loop Playback**: When checked, playback will automatically restart after completion
- **🎬 Smooth Movement**: When checked, mouse movements will be smoother and more natural
- **⚡ Playback Speed**: Choose from 0.5x, 1.0x, 1.5x, 2.0x, 3.0x speeds
- **🎯 Sampling Interval**: Adjust the sampling interval for mouse movements during recording (default 0.05 seconds)

### Statistics

Click the **"📊 Statistics"** button to view detailed information about the current recording, including:
- Total action count
- Movement event count
- Click count
- Scroll operation count
- Recording duration

## 🔧 Dependencies

Project dependencies (Python packages):

- **pynput** (>=1.7.6): For listening to and controlling mouse and keyboard operations

Installation command:
```bash
pip install pynput>=1.7.6
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

## 📁 Project Structure

```
clickPlus/
├── mouse_recorder_gui.py    # Main program file
├── requirements.txt         # Dependencies list
├── run_gui.bat             # Windows startup script
├── recordings/             # Recording files directory (auto-created)
├── README.md               # Chinese version
└── README_EN.md            # This file (English)
```

## 💡 Tips

1. **Recording Precision**: Adjusting the sampling interval controls recording precision. Smaller intervals record more movement trajectories but result in larger files
2. **Playback Speed**: For repetitive operations, use higher playback speeds (like 2.0x or 3.0x) to improve efficiency
3. **Smooth Movement**: Enabling smooth movement makes mouse trajectories more natural but may slightly extend playback time
4. **Loop Playback**: Suitable for operations that need to be repeated, such as game automation, automated testing, etc.

## ⚠️ Notes

1. The program may require administrator privileges to fully control the mouse (some systems may require this)
2. When recording, ensure you don't accidentally trigger other programs to avoid recording unwanted operations
3. When playing back, ensure the target window is active
4. It's recommended to test playback functionality before recording to ensure the program works correctly

## 🐛 Frequently Asked Questions

**Q: Program won't start?**  
A: Make sure you have Python 3.6+ installed and all dependency packages. Check if the virtual environment is correctly created.

**Q: Recording doesn't respond?**  
A: Ensure the program window is active and no other program is occupying mouse events.

**Q: Mouse doesn't move during playback?**  
A: Check if you have administrator privileges. Some systems require administrator privileges to control the mouse.

**Q: Hotkeys don't respond?**  
A: Ensure the program window is active. Some hotkeys may be occupied by other programs.

## 📝 License

This project uses an open-source license and is free to use and modify.

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📧 Contact

For questions or suggestions, please contact via GitHub Issues.

---

**Enjoy the fun of automation!** 🎉

