# Setup Checklist for fMRI Visual Task

Use this checklist to ensure everything is properly configured before running your study.

## Pre-Study Setup (Do Once)

### ✅ Step 1: Verify Installation

- [ ] Python 3.8 or higher is installed
  - Check: Run `python --version` or `python3 --version` in terminal
- [ ] Pygame is installed
  - Check: Run `python -c "import pygame; print('OK')"` (should print "OK")
- [ ] All required files are present:
  - [ ] `mvast_fmri_task.py`
  - [ ] `images/` folder with all image files
  - [ ] `requirements.txt`

### ✅ Step 2: Verify Image Files

- [ ] Blue-yellow images present (if using blue-yellow color scheme):
  - [ ] `images/acheck_by.png`
  - [ ] `images/acheck_by_.png`
  - [ ] `images/checker_by.png`

- [ ] Black-white images present (if using black-white color scheme):
  - [ ] `images/acheck_bw.png`
  - [ ] `images/acheck_bw_.png`
  - [ ] `images/checker_bw.png`

### ✅ Step 3: Initial Configuration

1. [ ] Run the application once: `python mvast_fmri_task.py`
2. [ ] Press ESC to exit (this creates the config file)
3. [ ] Locate `mvast_fmri_task_config.json` file
4. [ ] Configure the following settings:

   **Required Settings:**
   - [ ] `trigger_character`: Set to match your scanner (common: "=", "5", "t", "T")
   - [ ] `color_scheme`: Set to "blue_yellow" or "black_white"
   
   **Optional Settings:**
   - [ ] `start_mode`: "manual", "trigger", or "both" (default: "both")
   - [ ] `instruction_duration`: Duration in seconds (default: 10.0)
   - [ ] `instruction_text`: Custom instruction text (optional)

5. [ ] Save the configuration file
6. [ ] Test the configuration by running the application again

### ✅ Step 4: Test Configuration

- [ ] Application goes fullscreen when started
- [ ] "Ready to Start" screen appears
- [ ] Manual start works (SPACEBAR)
- [ ] Trigger start works (if configured - test by pressing trigger character key)
- [ ] Instruction screen appears after start (blue background, yellow text)
- [ ] Fixation cross appears correctly (blue background, yellow plus for blue-yellow mode)
- [ ] Checkerboard flashes correctly (8 Hz)
- [ ] ESC key cancels the task

### ✅ Step 5: Scanner Setup (If Using Scanner Trigger)

- [ ] Verify scanner trigger character matches config file
- [ ] Test scanner connection to presentation computer
- [ ] Verify trigger signal is received (check terminal output)
- [ ] If using serial port: verify port name and install pyserial

## Per-Participant Checklist

For each participant, you only need to:

1. [ ] Launch the application: `python mvast_fmri_task.py`
2. [ ] Wait for "Ready to Start" screen
3. [ ] Start the task (SPACEBAR or wait for scanner trigger)
4. [ ] Monitor that task completes successfully

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Python not found | Use `python3` instead of `python` |
| Pygame not installed | Run `pip install pygame` |
| Images not found | Verify `images/` folder exists with all required files |
| Trigger not working | Check `trigger_character` in config matches scanner |
| Wrong colors | Check `color_scheme` in config |
| Can't exit | Press ESC key |

## Dependencies Summary

**Required:**
- Python 3.8+
- pygame (install with: `pip install pygame`)

**Optional:**
- pyserial (only if using serial port triggers: `pip install pyserial`)

## Configuration File Location

The configuration file is created automatically on first run:
- **Location**: Same folder as `mvast_fmri_task.py`
- **Filename**: `mvast_fmri_task_config.json`
- **When to edit**: Once at the beginning of your study
- **When NOT to edit**: Between participants (unless changing study parameters)

---

**Remember:** Configuration is set once per study and reused for all participants!

