# M-VAST fMRI Visual Task - Presentation Computer Application

A Python-based visual stimulus presentation program designed for fMRI experiments. This application presents alternating fixation and flashing checkerboard stimuli synchronized with MRI scanner triggers.

> **📋 Quick Setup Guide:** See [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) for a step-by-step setup checklist.

## Overview

This program is designed to run on a **presentation computer** that is mirrored to a screen visible to participants inside an MRI scanner. The task consists of:

- **5 cycles** of alternating conditions
- Each cycle: **20 seconds fixation** + **20 seconds flashing checkerboard** (8 Hz)
- Total task duration: **200 seconds** (3 minutes 20 seconds)

## ⚠️ Important Safety Information

**Before using this task with participants, please review the following safety considerations in addition to your study protocol and local Institutional Review Board (IRB) requirements:**

- **Migraine History**: Participants with a history of migraine or photosensitivity should **NOT** perform this task, as flashing visual stimuli may trigger adverse reactions.
- **Adverse Events**: Visual flashing stimuli may cause discomfort, headaches, or other adverse reactions in some individuals. Researchers should be prepared to monitor participants and respond to any adverse events.
- **Participant Control**: Participants can stop the task at any time using the standard methods used at each institution/MRI facility. Ensure participants are informed of these stopping procedures before beginning the task.
- **Participant Responsibility**: Participants should be informed that they participate at their own risk and should immediately stop the task if they experience any discomfort, dizziness, nausea, or other adverse symptoms.
- **Researcher Monitoring**: Researchers should monitor participants throughout the task and be prepared to stop the task immediately if any adverse reactions occur.

**Best Practices:**
- Always obtain informed consent before participation
- Screen participants for contraindications (migraine history, photosensitivity, etc.)
- Provide clear instructions about the ability to stop at any time
- Have a researcher present to monitor for adverse reactions
- Ensure participants understand they can withdraw at any time without penalty

## Features

- ✅ **Cross-platform**: Compatible with Windows (all versions including Windows 11) and macOS
- ✅ **Fullscreen presentation**: Automatically enters fullscreen mode when running
- ✅ **Dual start modes**:
  - Manual start via **SPACEBAR** press
  - Automatic start via **scanner trigger signal** (configurable character)
- ✅ **Easy cancellation**: Press **ESC** at any time to stop the task
- ✅ **Configurable trigger**: Modify trigger character for different scanner setups
- ✅ **Serial port support**: Optional serial port trigger input (for advanced setups)

## Requirements

### Required Software

- **Python 3.8 or higher**
  - Download from [python.org/downloads](https://www.python.org/downloads/)
  - On Windows: Can also install from Microsoft Store

### Required Python Packages

- **pygame** (version 2.0.0 or higher)
  - Install with: `pip install pygame` or `python -m pip install pygame`
  - **Required for**: Visual presentation and fullscreen display

### Optional Python Packages

- **pyserial** (version 3.5 or higher)
  - Install with: `pip install pyserial`
  - **Only needed if**: Using serial port for scanner triggers (most scanners use keyboard simulation instead)

### Required Files

All of these files are included in the repository:

- `mvast_fmri_task.py` - Main application
- `images/` folder containing:
  - `acheck_by.png`, `acheck_by_.png` (for blue-yellow mode)
  - `acheck_bw.png`, `acheck_bw_.png` (for black-white mode)
  - `checker_by.png`, `checker_bw.png` (static checkerboards)

## Installation

Choose one of the installation methods below. **Option A** is recommended for beginners.

### Option A: Simple Installation (Recommended for Beginners)

**Best for users unfamiliar with programming or the terminal**

#### Step 1: Download the Files

1. Download this repository (or the required files)
2. Extract to a folder on your computer (e.g., Desktop or Documents)
3. Verify the `images` folder contains all required image files:

   **Required for blue-yellow color scheme (default):**
   - `acheck_by.png` - Checkerboard image 1
   - `acheck_by_.png` - Checkerboard image 2
   - `checker_by.png` - Static checkerboard (used if needed)
   
   **Required for black-white color scheme:**
   - `acheck_bw.png` - Checkerboard image 1
   - `acheck_bw_.png` - Checkerboard image 2
   - `checker_bw.png` - Static checkerboard (used if needed)
   
   **Note:** All images are included in the repository. If any are missing, re-download the repository.

#### Step 2: Install Python

**On Windows:**
1. Open Command Prompt (search for "cmd" in the Start menu)
2. Type `python` and press Enter
3. This will open the Microsoft Store where you can install Python
4. Click "Install" and wait for it to complete

**On Mac:**
1. Go to [python.org/downloads](https://python.org/downloads)
2. Download and install the latest version of Python
3. Follow the installation prompts

**Check Python installation:**
- Open Command Prompt (Windows) or Terminal (Mac)
- Type `python --version` or `python3 --version`
- You should see something like "Python 3.8.0" or higher

#### Step 3: Navigate to the Downloaded Files

You need to tell your computer where to find the fMRI task files.

**On Windows:**
1. Open Command Prompt
2. Type `cd Desktop\mvast_fmri_task` (or wherever you saved the files)
3. Press Enter

**On Mac:**
1. Open Terminal
2. Type `cd Desktop/mvast_fmri_task` (or wherever you saved the files)
3. Press Enter

**Verify you're in the right place:**
- On Windows: type `dir` and press Enter
- On Mac: type `ls` and press Enter

You should see:
- `mvast_fmri_task.py`
- `images/` folder
- `README.md`

#### Step 4: Install Required Packages

In the same terminal/command prompt window, type:

```bash
python -m pip install pygame
```

**If you get an error saying "python is not recognized":**
- Try using `python3` instead: `python3 -m pip install pygame`
- Use `python3` for all future commands if `python` doesn't work

**If you plan to use serial port triggers**, also install:

```bash
python -m pip install pyserial
```

#### Step 5: Run the Application

```bash
python mvast_fmri_task.py
```

Or if `python` doesn't work:

```bash
python3 mvast_fmri_task.py
```

The application will start in fullscreen mode!

### Option B: Python Virtual Environment (Standard)

**Best for users comfortable with Python development**

1. **Navigate to the project directory**
   ```bash
   cd path/to/mvast_fmri_task
   ```

2. **Create virtual environment**
   ```bash
   # Create virtual environment
   python -m venv fmri_env
   
   # Activate (Windows)
   .\fmri_env\Scripts\activate
   
   # Activate (macOS/Linux)
   source fmri_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install pygame
   # Optional: pip install pyserial
   ```

4. **Run the application**
   ```bash
   python mvast_fmri_task.py
   ```

### Option C: Conda Environment (For Researchers)

**Best for scientific computing environments**

1. **Navigate to the project directory**
   ```bash
   cd path/to/mvast_fmri_task
   ```

2. **Create Conda environment**
   ```bash
   conda create -n mvast_fmri_task python=3.9 pygame
   conda activate mvast_fmri_task
   ```

3. **Install additional dependencies if needed**
   ```bash
   pip install pyserial  # Optional, for serial port triggers
   ```

4. **Run the application**
   ```bash
   python mvast_fmri_task.py
   ```

## Initial Setup for Your Study (One-Time Configuration)

**⚠️ IMPORTANT: This setup should only be done once at the beginning of your study. The configuration will be saved and reused for all participants.**

### Step 1: Run the Application Once

1. **Launch the application** for the first time:
   ```bash
   python mvast_fmri_task.py
   ```
   (or `python3 mvast_fmri_task.py`)

2. **Press ESC** to exit immediately (this creates the default configuration file)

### Step 2: Configure for Your Study

1. **Locate the configuration file**: `mvast_fmri_task_config.json` (created in the same folder as the program)

2. **Open the file** in any text editor (Notepad, TextEdit, etc.)

3. **Edit the following settings** based on your study needs:

   ```json
   {
       "trigger_character": "=",        // Change to match your scanner (common: "5", "t", "T")
       "start_mode": "both",             // "manual", "trigger", or "both"
       "color_scheme": "blue_yellow",    // "blue_yellow" or "black_white"
       "instruction_duration": 10.0      // Duration in seconds for instruction screen
   }
   ```

4. **Save the file**

5. **Test the configuration** by running the application again and verifying:
   - The trigger character works (if using scanner trigger)
   - The color scheme is correct
   - The instruction screen appears

**That's it!** This configuration will be used for all participants in your study. You typically won't need to change it again unless you switch scanners or studies.

## Usage

### Starting the Task (For Each Participant)

1. **Launch the application**: Run `python mvast_fmri_task.py` (or `python3 mvast_fmri_task.py`)

2. **Wait for start screen**: The application will display a "Ready to Start" screen

3. **Start the task** using one of these methods:
   - Press **SPACEBAR** to start manually
   - Wait for the scanner trigger signal (if configured)

### During the Task

- The task runs automatically through 5 cycles
- Each cycle consists of:
  - **20 seconds** of fixation cross (+)
  - **20 seconds** of flashing checkerboard (8 Hz)
- Press **ESC** at any time to cancel the task

### Configuration

The application creates a configuration file (`mvast_fmri_task_config.json`) on first run. You can edit this file to customize settings:

```json
{
    "trigger_character": "=",
    "start_mode": "both",
    "color_scheme": "blue_yellow",
    "use_serial_port": false,
    "serial_port": null,
    "images_dir": "images",
    "fixation_image": null,
    "checkerboard_image1": null,
    "checkerboard_image2": null,
    "instruction_image": null,
    "instruction_duration": 10.0
}
```

**Common modifications:**

1. **Set color scheme**: Choose between blue-yellow or black-white task
   ```json
   "color_scheme": "blue_yellow"  // Blue and yellow images (default)
   "color_scheme": "black_white"  // Black and white images
   ```
   - This automatically sets the appropriate fixation and checkerboard images
   - For `blue_yellow`: Uses `checker_by.png` for fixation, `acheck_by.png` and `acheck_by_.png` for checkerboard
   - For `black_white`: Uses `checker_bw.png` for fixation, `acheck_bw.png` and `acheck_bw_.png` for checkerboard

2. **Change trigger character**: Default is "=", but scanners may use "5", "t", "T", etc.
   ```json
   "trigger_character": "5"
   ```

3. **Set start mode**: Choose how the task starts
   ```json
   "start_mode": "manual"    // Only start with SPACEBAR
   "start_mode": "trigger"   // Only start with scanner trigger
   "start_mode": "both"      // Start with either (default)
   ```

4. **Customize instruction text** (displayed during dummy scans/discarded acquisitions):
   ```json
   "instruction_text": "Your custom instructions here\n\nLine 2\n\nLine 3",
   "instruction_duration": 10.0
   ```
   - By default, the instruction screen shows text on a blue background (yellow text)
   - You can customize the text by setting `instruction_text` in the config
   - Use `\n` for new lines, `\n\n` for blank lines between paragraphs
   - The duration is in seconds (default: 10.0)
   - This screen is shown immediately after the start signal, before the first cycle
   
   **Note:** If you want to use an image instead of text, set:
   ```json
   "instruction_image": "instruction.png"  // Place image in images/ folder
   ```

5. **Add instruction image** (alternative to text, optional):
   ```json
   "instruction_image": "instruction.png",
   "instruction_duration": 10.0
   ```
   - Place your instruction image in the `images/` folder
   - If both `instruction_image` and `instruction_text` are set, the image takes precedence

6. **Use serial port for triggers** (advanced):
   ```json
   "use_serial_port": true,
   "serial_port": "COM3"
   ```
   (On Mac/Linux, use something like `"/dev/ttyUSB0"`)

### Setting Up for Your Scanner

Different fMRI scanners use different methods to send trigger signals:

1. **Keyboard simulation** (most common): Scanner sends trigger as a keyboard key press
   - Edit `mvast_fmri_task_config.json` and set `"trigger_character"` to match your scanner's trigger key
   - Common values: "5", "t", "T"

2. **Serial port** (less common): Scanner sends trigger via serial/USB connection
   - Edit `mvast_fmri_task_config.json`:
     - Set `"use_serial_port": true`
     - Set `"serial_port"` to your port name (e.g., "COM3" on Windows, "/dev/ttyUSB0" on Mac)
   - Install pyserial: `pip install pyserial`

3. **Network trigger** (rare): Would require custom modifications to the code

## Troubleshooting

### "Python is not recognized" error

- Try using `python3` instead of `python` in all commands
- Make sure Python is properly installed and added to PATH
- On Windows, you may need to restart Command Prompt after installing Python

### "No module named pygame" error

- Make sure you ran the `pip install pygame` command
- Try: `python3 -m pip install pygame` if `python` doesn't work
- Make sure you're in the correct directory

### Images not found

- Verify the `images` folder exists and contains all required files:
  - **For blue-yellow mode:** `acheck_by.png`, `acheck_by_.png`, `checker_by.png`
  - **For black-white mode:** `acheck_bw.png`, `acheck_bw_.png`, `checker_bw.png`
  - `instruction.png` (optional, only if using custom instruction image)
- Check that the images are in the `images/` folder in the same directory as `mvast_fmri_task.py`
- If images are missing, re-download the repository or contact the development team

### Application doesn't go fullscreen

- Make sure your display is properly configured
- Try running as administrator (Windows) or with appropriate permissions (Mac)
- Check that your graphics drivers are up to date

### Trigger signal not working

- Verify the trigger character in `mvast_fmri_task_config.json` matches your scanner's output
- Test by manually pressing the trigger character key on the keyboard
- If using serial port, verify the port name is correct
- Check that the scanner is properly connected to the presentation computer

### Task runs too fast or too slow

- The timing is controlled by the code constants (FIXATION_DURATION, CHECKERBOARD_DURATION, FLASH_FREQUENCY)
- These are set to 20 seconds, 20 seconds, and 8 Hz respectively
- Contact the developer if you need to modify these timings

### Can't exit fullscreen

- Press **ESC** to cancel the task at any time
- On some systems, you may need to press Alt+F4 (Windows) or Cmd+Q (Mac) to force quit

## Task Structure

The task consists of:

1. **Instruction Screen** (always shown, configurable duration, default 10s):
   - Displayed during dummy scans/discarded acquisitions
   - Shown immediately after start signal, before first cycle
   - Blue background with yellow text (for blue-yellow mode) or black background with white text (for black-white mode)
   - Default text explains the task, but can be customized via `instruction_text` in config file
   - Configure duration via `instruction_duration` in config file

2. **5 cycles** of alternating conditions:

```
[Instruction Screen - 10s] (default)
Cycle 1: [20s Fixation] → [20s Checkerboard @ 8 Hz]
Cycle 2: [20s Fixation] → [20s Checkerboard @ 8 Hz]
Cycle 3: [20s Fixation] → [20s Checkerboard @ 8 Hz]
Cycle 4: [20s Fixation] → [20s Checkerboard @ 8 Hz]
Cycle 5: [20s Fixation] → [20s Checkerboard @ 8 Hz]
```

**Total duration**: 
- Default: 210 seconds (10s instruction + 200s task = 3 minutes 30 seconds)
- Task cycles only: 200 seconds (3 minutes 20 seconds)

## Technical Details

- **Programming language**: Python 3.8+
- **Graphics library**: Pygame
- **Display mode**: Fullscreen (matches primary display resolution)
- **Frame rate**: 60 FPS (for smooth checkerboard flashing)
- **Checkerboard frequency**: 8 Hz (16 frame changes per second)

## File Structure

```
mvast_fmri_task/
├── mvast_fmri_task.py              # Main application
├── mvast_fmri_task_config.json     # Configuration file (created on first run)
├── requirements.txt                 # Python dependencies
├── LICENSE                          # MIT License
├── images/                          # Image assets folder
│   ├── acheck_by.png               # Blue-yellow checkerboard 1
│   ├── acheck_by_.png              # Blue-yellow checkerboard 2
│   ├── acheck_bw.png                # Black-white checkerboard 1
│   ├── acheck_bw_.png               # Black-white checkerboard 2
│   ├── checker_by.png               # Blue-yellow static checkerboard
│   └── checker_bw.png               # Black-white static checkerboard
├── README.md                        # This file (main documentation)
├── QUICK_START.md                   # Quick reference guide
├── SETUP_CHECKLIST.md               # Setup checklist
└── CODE_REVIEW_SUMMARY.md           # Code review summary
```

## Credits & Attribution

**Developed by:** eAi Solutions

**Based on:** M-VAST 3 (Michigan Visual Aversion Stress Test)  
Original software by: Brock Pluimer (University of California, Irvine) & Steven Harte (University of Michigan)  
Original repository: https://github.com/brockpluimer/mvast3

This fMRI task application was adapted and modified from the M-VAST 3 platform for fMRI scanner compatibility and presentation computer use.

## Support

For questions, issues, or feature requests related to this fMRI task application, please contact:
- **eAi Solutions** - Development and support

For questions about the original M-VAST 3 methodology, please contact:
- **Brock Pluimer** - bpluimer@hs.uci.edu

## License

This software is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

**Version**: v1.0_2025  
**Developed by**: eAi Solutions

