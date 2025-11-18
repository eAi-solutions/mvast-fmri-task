# Quick Start Guide - fMRI Visual Task

## Fastest Way to Get Started

### 1. Install Python (if not already installed)

**Windows:**
- Open Microsoft Store, search for "Python", install it
- OR download from [python.org](https://www.python.org/downloads/)

**Mac:**
- Download from [python.org](https://www.python.org/downloads/)
- OR install via Homebrew: `brew install python3`

### 2. Install Pygame

Open Terminal (Mac) or Command Prompt (Windows) and run:

```bash
python -m pip install pygame
```

Or if that doesn't work:

```bash
python3 -m pip install pygame
```

### 3. Navigate to the Program Folder

```bash
cd path/to/fmri_task
```

### 4. Run the Program

```bash
python fmri_task.py
```

Or:

```bash
python3 fmri_task.py
```

### 5. Start the Task

- Press **SPACEBAR** to start manually
- OR wait for scanner trigger (if configured)

### 6. Stop the Task

- Press **ESC** at any time to cancel

## That's It!

The program will:
- Automatically go fullscreen
- Show a ready screen
- Wait for your start signal
- Run 5 cycles of fixation + checkerboard
- Complete in ~3 minutes 20 seconds

## Configuration

On first run, a `fmri_task_config.json` file will be created. Edit it to change the trigger character if needed.

## Need Help?

See the full [README.md](README.md) for detailed instructions and troubleshooting.

