# -*- coding: utf-8 -*-
"""
M-VAST fMRI Visual Task - Presentation Computer Application
Compatible with Windows (all versions) and macOS

Developed by: eAi Solutions
Based on: M-VAST 3 (Michigan Visual Aversion Stress Test)
Original software by: Brock Pluimer & Steven Harte
Original repository: https://github.com/brockpluimer/mvast3

This program presents visual stimuli for fMRI experiments:
- 5 cycles of alternating fixation (20s) and flashing checkerboard (20s)
- Can be started manually (spacebar) or via scanner trigger signal
- Instruction screen during dummy scans
- Configurable color schemes (blue-yellow or black-white)
"""

import pygame
import sys
import os
import time
import json
import threading
import queue
from datetime import datetime

# --- Application Constants ---
APP_VERSION = "v1.0_2025"
CONFIG_FILE = "mvast_fmri_task_config.json"

# Task Parameters
NUM_CYCLES = 5
FIXATION_DURATION = 20.0  # seconds
CHECKERBOARD_DURATION = 20.0  # seconds
FLASH_FREQUENCY = 8.0  # Hz (8 Hz = 8 flashes per second)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)  # Blue background for fixation
YELLOW = (255, 255, 0)  # Yellow plus sign

# Default configuration
DEFAULT_CONFIG = {
    "trigger_character": "=",  # Default trigger character (can be changed per scanner)
    "start_mode": "both",  # Options: "manual", "trigger", or "both" (allows either)
    "color_scheme": "blue_yellow",  # Options: "blue_yellow" or "black_white"
    "use_serial_port": False,  # Set to True to use serial port for triggers
    "serial_port": None,  # e.g., "COM3" (Windows) or "/dev/ttyUSB0" (Mac/Linux)
    "images_dir": "images",
    "fixation_image": None,  # Auto-set based on color_scheme, or specify manually
    "checkerboard_image1": None,  # Auto-set based on color_scheme
    "checkerboard_image2": None,  # Auto-set based on color_scheme
    "instruction_image": None,  # Path to instruction image (e.g., "instruction.png"). If None, renders text
    "instruction_text": None,  # Custom instruction text (if None, uses default). Only used if instruction_image is None
    "instruction_duration": 10.0  # Duration in seconds (for dummy scans/discarded acquisitions)
}


# --- Configuration Management ---
def load_config():
    """Load configuration from file, or create default if not exists."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            # Merge with defaults to ensure all keys exist
            merged = DEFAULT_CONFIG.copy()
            merged.update(config)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            merged = DEFAULT_CONFIG.copy()
    else:
        # Create default config file
        merged = DEFAULT_CONFIG.copy()
        save_config(merged)
    
    # Auto-configure images based on color_scheme if not explicitly set
    color_scheme = merged.get("color_scheme", "blue_yellow").lower()
    
    # Validate color_scheme
    if color_scheme not in ["blue_yellow", "black_white"]:
        print(f"Warning: Invalid color_scheme '{color_scheme}'. Using default 'blue_yellow'.")
        color_scheme = "blue_yellow"
        merged["color_scheme"] = color_scheme
    
    if color_scheme == "black_white":
        if not merged.get("checkerboard_image1"):
            merged["checkerboard_image1"] = "acheck_bw.png"
        if not merged.get("checkerboard_image2"):
            merged["checkerboard_image2"] = "acheck_bw_.png"
        # Fixation will be rendered programmatically (black background, white plus)
        # Only set if explicitly provided
    else:  # blue_yellow (default)
        if not merged.get("checkerboard_image1"):
            merged["checkerboard_image1"] = "acheck_by.png"
        if not merged.get("checkerboard_image2"):
            merged["checkerboard_image2"] = "acheck_by_.png"
        # Fixation will be rendered programmatically (blue background, yellow plus)
        # Only set if explicitly provided
    
    # Validate start_mode
    start_mode = merged.get("start_mode", "both").lower()
    if start_mode not in ["manual", "trigger", "both"]:
        print(f"Warning: Invalid start_mode '{start_mode}'. Using default 'both'.")
        merged["start_mode"] = "both"
    
    # Validate instruction_duration
    try:
        duration = float(merged.get("instruction_duration", 10.0))
        if duration < 0:
            print(f"Warning: instruction_duration must be >= 0. Using default 10.0.")
            merged["instruction_duration"] = 10.0
        else:
            merged["instruction_duration"] = duration
    except (ValueError, TypeError):
        print(f"Warning: Invalid instruction_duration. Using default 10.0.")
        merged["instruction_duration"] = 10.0
    
    return merged


def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving config: {e}")


# --- Trigger Input Handler (for scanner triggers) ---
class TriggerInputHandler:
    """Handles trigger input from scanner via keyboard simulation or serial port."""
    
    def __init__(self, trigger_char, config):
        self.trigger_char = trigger_char.lower()  # Convert to lowercase for comparison
        self.config = config
        self.trigger_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.use_serial = config.get("use_serial_port", False)
        self.serial_port = config.get("serial_port", None)
        
    def start(self):
        """Start the trigger input thread."""
        self.running = True
        
        if self.use_serial and self.serial_port:
            # Use serial port for trigger input
            self.thread = threading.Thread(target=self._read_serial_triggers, daemon=True)
            print(f"Trigger input handler started. Listening on serial port: {self.serial_port}")
        else:
            # Use keyboard input simulation (scanner triggers often come as keyboard events)
            self.thread = threading.Thread(target=self._read_keyboard_triggers, daemon=True)
            print(f"Trigger input handler started. Listening for keyboard character '{self.trigger_char}'")
        
        self.thread.start()
        
    def stop(self):
        """Stop the trigger input thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def _read_keyboard_triggers(self):
        """
        Read trigger signals from keyboard input.
        Note: Many fMRI scanners send triggers as keyboard events.
        This monitors for the configured trigger character.
        """
        # For keyboard-based triggers, we'll monitor pygame events in the main loop
        # This thread exists for future serial port support
        # The actual keyboard checking happens in wait_for_start via pygame events
        while self.running:
            time.sleep(0.1)
    
    def _read_serial_triggers(self):
        """Read trigger signals from serial port (if configured)."""
        ser = None
        try:
            import serial
            ser = serial.Serial(self.serial_port, baudrate=9600, timeout=0.1)
            print(f"Serial port {self.serial_port} opened successfully.")
            
            while self.running:
                try:
                    if ser.in_waiting > 0:
                        data = ser.read(1)
                        if data:
                            char = data.decode('utf-8', errors='ignore').lower()
                            if char == self.trigger_char:
                                self.trigger_queue.put(True)
                                print(f"Trigger received via serial port!")
                except Exception as e:
                    print(f"Serial read error: {e}")
                time.sleep(0.01)
        except ImportError:
            print("WARNING: pyserial not installed. Install with: pip install pyserial")
            print("Falling back to keyboard input mode.")
            self._read_keyboard_triggers()
        except Exception as e:
            print(f"Serial port error: {e}. Falling back to keyboard input.")
            self._read_keyboard_triggers()
        finally:
            # Ensure serial port is closed even if an error occurs
            if ser is not None and ser.is_open:
                try:
                    ser.close()
                    print("Serial port closed.")
                except Exception as e:
                    print(f"Error closing serial port: {e}")
    
    def check_trigger(self):
        """Check if a trigger has been received (non-blocking)."""
        try:
            self.trigger_queue.get_nowait()
            return True
        except queue.Empty:
            return False


# --- Image Loading Functions ---
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and packaged app."""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_fixation_image(screen_width, screen_height, image_path=None, color_scheme="blue_yellow"):
    """Load fixation image or create a rendered plus sign based on color scheme."""
    # If image_path is explicitly provided, try to load it
    if image_path:
        images_dir = resource_path("images")
        full_path = os.path.join(images_dir, image_path) if not os.path.isabs(image_path) else image_path
        
        if os.path.exists(full_path):
            try:
                img = pygame.image.load(full_path)
                img = img.convert()
                img = pygame.transform.scale(img, (screen_width, screen_height))
                print(f"Fixation image loaded: {image_path}")
                return img
            except Exception as e:
                print(f"Warning: Could not load fixation image {full_path}: {e}")
        else:
            print(f"Warning: Fixation image not found: {full_path}")
    
    # Create a rendered fixation based on color scheme
    surface = pygame.Surface((screen_width, screen_height))
    
    # Set background color based on scheme
    if color_scheme.lower() == "black_white":
        bg_color = BLACK
        cross_color = WHITE
    else:  # blue_yellow (default)
        bg_color = BLUE
        cross_color = YELLOW
    
    surface.fill(bg_color)
    
    # Calculate size based on screen dimensions
    cross_size = min(screen_width, screen_height) // 8
    line_width = max(3, cross_size // 20)
    
    center_x, center_y = screen_width // 2, screen_height // 2
    
    # Draw horizontal line of plus sign
    pygame.draw.rect(surface, cross_color, 
                    (center_x - cross_size // 2, center_y - line_width // 2,
                     cross_size, line_width))
    # Draw vertical line of plus sign
    pygame.draw.rect(surface, cross_color,
                    (center_x - line_width // 2, center_y - cross_size // 2,
                     line_width, cross_size))
    
    scheme_name = "blue-yellow" if color_scheme.lower() == "blue_yellow" else "black-white"
    print(f"Fixation created: {scheme_name} (background: {scheme_name.split('-')[0]}, plus: {scheme_name.split('-')[1]})")
    
    return surface


def load_instruction_image(screen_width, screen_height, image_path=None, color_scheme="blue_yellow", instruction_text=None):
    """
    Load instruction image or create a rendered instruction screen.
    If image_path is provided, loads that image. Otherwise, renders text instructions.
    """
    # If image_path is explicitly provided, try to load it
    if image_path:
        images_dir = resource_path("images")
        full_path = os.path.join(images_dir, image_path) if not os.path.isabs(image_path) else image_path
        
        if os.path.exists(full_path):
            try:
                img = pygame.image.load(full_path)
                img = img.convert()
                img = pygame.transform.scale(img, (screen_width, screen_height))
                print(f"Instruction image loaded: {image_path}")
                return img
            except Exception as e:
                print(f"Warning: Could not load instruction image {full_path}: {e}")
        else:
            print(f"Warning: Instruction image not found: {full_path}")
    
    # Create rendered instruction screen with text
    surface = pygame.Surface((screen_width, screen_height))
    
    # Set background color based on scheme
    if color_scheme.lower() == "black_white":
        bg_color = BLACK
        text_color = WHITE
    else:  # blue_yellow (default)
        bg_color = BLUE
        text_color = YELLOW
    
    surface.fill(bg_color)
    
    # Default instruction text if none provided
    if not instruction_text:
        instruction_text = """For the next several minutes, you will see a fixation cross alternate with a flashing checkerboard.


Please keep your eyes open and fixed on the center of the screen.


The task will start shortly."""
    
    # Calculate font size based on screen
    screen_height_px = screen_height
    base_font_size = int(screen_height_px / 25)
    font_size = max(24, base_font_size)
    
    try:
        font = pygame.font.Font(None, font_size)
    except:
        font = pygame.font.SysFont("arial", font_size)
    
    # Split text into lines and render
    lines = [line.strip() for line in instruction_text.split('\n')]
    rendered_lines = []
    total_height = 0
    
    for line in lines:
        if line:
            rendered = font.render(line, True, text_color)
            rendered_lines.append(rendered)
            total_height += rendered.get_height() + 10
        else:
            rendered_lines.append(None)
            total_height += 20
    
    # Center vertically
    y_start = (screen_height - total_height) // 2
    current_y = y_start
    
    # Draw lines
    for rendered in rendered_lines:
        if rendered:
            rect = rendered.get_rect(centerx=screen_width // 2, top=current_y)
            surface.blit(rendered, rect)
            current_y += rendered.get_height() + 10
        else:
            current_y += 20
    
    scheme_name = "blue-yellow" if color_scheme.lower() == "blue_yellow" else "black-white"
    print(f"Instruction screen created: {scheme_name} (background: {scheme_name.split('-')[0]}, text: {scheme_name.split('-')[1]})")
    
    return surface


def load_checkerboard_images(screen_width, screen_height, img1_path, img2_path):
    """Load and scale the two checkerboard images for flashing."""
    images_dir = resource_path("images")
    img1_full = os.path.join(images_dir, img1_path)
    img2_full = os.path.join(images_dir, img2_path)
    
    try:
        if not os.path.exists(img1_full):
            raise FileNotFoundError(f"Image 1 not found: {img1_full}")
        if not os.path.exists(img2_full):
            raise FileNotFoundError(f"Image 2 not found: {img2_full}")
            
        img1 = pygame.image.load(img1_full)
        img2 = pygame.image.load(img2_full)
        img1 = img1.convert()
        img2 = img2.convert()
        
        # Scale to screen size
        img1 = pygame.transform.scale(img1, (screen_width, screen_height))
        img2 = pygame.transform.scale(img2, (screen_width, screen_height))
        
        return img1, img2
    except Exception as e:
        print(f"Error loading checkerboard images: {e}")
        return None, None


# --- Display Functions ---
def show_message(screen, text, wait_for_input=True, escape_cancels=True):
    """Display a message on screen and optionally wait for input."""
    if not screen:
        print(f"Message: {text}")
        return True
        
    screen.fill(BLACK)
    
    # Calculate font size based on screen
    screen_height = screen.get_height()
    font_size = max(24, int(screen_height / 25))
    
    try:
        font = pygame.font.Font(None, font_size)
    except:
        font = pygame.font.SysFont("arial", font_size)
    
    # Render text lines
    lines = [line.strip() for line in text.split('\n')]
    rendered_lines = []
    total_height = 0
    
    for line in lines:
        if line:
            rendered = font.render(line, True, WHITE)
            rendered_lines.append(rendered)
            total_height += rendered.get_height() + 10
        else:
            rendered_lines.append(None)
            total_height += 20
    
    # Center vertically
    y_start = (screen_height - total_height) // 2
    
    # Draw lines
    current_y = y_start
    for rendered in rendered_lines:
        if rendered:
            rect = rendered.get_rect(centerx=screen.get_width() // 2, top=current_y)
            screen.blit(rendered, rect)
            current_y += rendered.get_height() + 10
        else:
            current_y += 20
    
    pygame.display.flip()
    
    if wait_for_input:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True
                    if escape_cancels and event.key == pygame.K_ESCAPE:
                        return False
            time.sleep(0.01)
    
    return True


def show_fixation(screen, fixation_image, duration, escape_cancels=True):
    """Display fixation cross/image for specified duration with precise timing."""
    if not screen:
        return True
        
    screen.fill(BLACK)
    screen.blit(fixation_image, (0, 0))
    pygame.display.flip()
    
    start_time = time.perf_counter()
    end_time = start_time + duration
    
    while time.perf_counter() < end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if escape_cancels and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        # Reduced sleep for better timing precision
        time.sleep(0.005)
    
    return True


def show_instruction_image(screen, instruction_image, duration, escape_cancels=True):
    """Display instruction image for specified duration (during dummy scans) with precise timing."""
    if not screen or not instruction_image:
        return True
    
    screen.fill(BLACK)
    screen.blit(instruction_image, (0, 0))
    pygame.display.flip()
    
    start_time = time.perf_counter()
    end_time = start_time + duration
    
    while time.perf_counter() < end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if escape_cancels and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        # Reduced sleep for better timing precision
        time.sleep(0.005)
    
    return True


def show_flashing_checkerboard(screen, img1, img2, duration, frequency, escape_cancels=True):
    """
    Display alternating checkerboard images at specified frequency.
    Uses high-precision timing to ensure accurate flash frequency.
    """
    if not screen or not img1 or not img2:
        return True
    
    frame_duration = 1.0 / frequency / 2.0  # Half period for each image (125ms for 8 Hz)
    start_time = time.perf_counter()
    end_time = start_time + duration
    current_image = True  # True for img1, False for img2
    last_flip_time = start_time
    frame_count = 0
    
    while time.perf_counter() < end_time:
        # Check for events (non-blocking)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if escape_cancels and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        # Flip images at the specified frequency with precise timing
        current_time = time.perf_counter()
        if current_time >= last_flip_time + frame_duration:
            screen.fill(BLACK)
            if current_image:
                screen.blit(img1, (0, 0))
            else:
                screen.blit(img2, (0, 0))
            pygame.display.flip()
            current_image = not current_image
            frame_count += 1
            # Use additive timing to prevent drift accumulation
            last_flip_time += frame_duration
        
        # Small sleep to prevent CPU spinning (minimal impact on timing)
        time.sleep(0.0001)  # Reduced from 0.001 for better precision
    
    # Verify timing accuracy (for debugging/logging)
    actual_duration = time.perf_counter() - start_time
    expected_frames = int(duration * frequency * 2)  # 2 frames per flash cycle
    if abs(frame_count - expected_frames) > 2:  # Allow small tolerance
        print(f"  Warning: Frame count ({frame_count}) differs from expected ({expected_frames})")
    
    return True


# --- Wait for Start ---
def wait_for_start(screen, trigger_handler, config, escape_cancels=True):
    """Wait for start signal based on configured start mode."""
    trigger_char = config.get("trigger_character", "=")
    start_mode = config.get("start_mode", "both").lower()
    
    # Build message based on start mode
    if start_mode == "manual":
        message = f"""fMRI Visual Task - Ready to Start

Waiting for manual start...

Press SPACEBAR to start

Press ESC to cancel"""
    elif start_mode == "trigger":
        message = f"""fMRI Visual Task - Ready to Start

Waiting for scanner trigger signal...

Trigger character: '{trigger_char}'

Press ESC to cancel"""
    else:  # "both" - default
        message = f"""fMRI Visual Task - Ready to Start

Waiting for start signal...

Press SPACEBAR to start manually
OR
Wait for scanner trigger signal (character: '{trigger_char}')

Press ESC to cancel"""
    
    screen.fill(BLACK)
    
    # Calculate font size
    screen_height = screen.get_height()
    font_size = max(24, int(screen_height / 25))
    
    try:
        font = pygame.font.Font(None, font_size)
    except:
        font = pygame.font.SysFont("arial", font_size)
    
    # Render message
    lines = [line.strip() for line in message.split('\n')]
    rendered_lines = []
    total_height = 0
    
    for line in lines:
        if line:
            rendered = font.render(line, True, WHITE)
            rendered_lines.append(rendered)
            total_height += rendered.get_height() + 10
    
    y_start = (screen_height - total_height) // 2
    current_y = y_start
    
    for rendered in rendered_lines:
        rect = rendered.get_rect(centerx=screen.get_width() // 2, top=current_y)
        screen.blit(rendered, rect)
        current_y += rendered.get_height() + 10
    
    pygame.display.flip()
    
    # Wait for start signal based on mode
    while True:
        # Check keyboard events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                # Manual start (spacebar) - only if mode is "manual" or "both"
                if event.key == pygame.K_SPACE and start_mode in ["manual", "both"]:
                    print("Start signal received: SPACEBAR")
                    return True
                # Trigger character start - only if mode is "trigger" or "both"
                if start_mode in ["trigger", "both"]:
                    if event.unicode and event.unicode.lower() == trigger_char.lower():
                        print(f"Start signal received: Trigger character '{trigger_char}'")
                        return True
                if escape_cancels and event.key == pygame.K_ESCAPE:
                    return False
        
        # Check for trigger signal from serial port (if configured and mode allows triggers)
        if start_mode in ["trigger", "both"] and trigger_handler and trigger_handler.check_trigger():
            print(f"Start signal received: Serial port trigger")
            return True
        
        time.sleep(0.01)


# --- Main Task Execution ---
def run_task(screen, config):
    """Execute the main fMRI task."""
    print("=" * 60)
    print(f"fMRI Visual Task - Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load images
    screen_width, screen_height = screen.get_size()
    
    # Load fixation image
    color_scheme = config.get("color_scheme", "blue_yellow")
    fixation_image = load_fixation_image(screen_width, screen_height, config.get("fixation_image"), color_scheme)
    
    # Load or create instruction screen (for dummy scans)
    instruction_image = None
    instruction_duration = config.get("instruction_duration", 10.0)
    instruction_text = config.get("instruction_text")
    
    # Always create instruction screen (either from image or rendered text)
    # If instruction_image is None, it will render text automatically
    instruction_image = load_instruction_image(
        screen_width, screen_height, 
        config.get("instruction_image"), 
        color_scheme,
        instruction_text
    )
    
    if instruction_image:
        print(f"Instruction screen ready (duration: {instruction_duration}s)")
    else:
        print("Warning: Could not create instruction screen")
    
    # Load checkerboard images
    checkerboard1, checkerboard2 = load_checkerboard_images(
        screen_width, screen_height,
        config["checkerboard_image1"],
        config["checkerboard_image2"]
    )
    
    # Validate all critical images are loaded before starting task
    if not checkerboard1 or not checkerboard2:
        error_msg = f"ERROR: Could not load checkerboard images.\n\n"
        error_msg += f"Expected: {config['checkerboard_image1']}, {config['checkerboard_image2']}\n\n"
        error_msg += "Please verify images exist in the 'images' folder.\n\n"
        error_msg += "Press SPACEBAR to exit."
        show_message(screen, error_msg, wait_for_input=True, escape_cancels=True)
        return False
    
    if not fixation_image:
        error_msg = "ERROR: Could not create or load fixation image.\n\n"
        error_msg += "Press SPACEBAR to exit."
        show_message(screen, error_msg, wait_for_input=True, escape_cancels=True)
        return False
    
    # Validate timing parameters
    if CHECKERBOARD_DURATION <= 0 or FIXATION_DURATION <= 0:
        error_msg = "ERROR: Invalid timing parameters.\n\n"
        error_msg += "Press SPACEBAR to exit."
        show_message(screen, error_msg, wait_for_input=True, escape_cancels=True)
        return False
    
    # Initialize trigger handler
    trigger_handler = None
    if config.get("trigger_character"):
        trigger_handler = TriggerInputHandler(config["trigger_character"], config)
        trigger_handler.start()
    
    try:
        # Wait for start signal
        if not wait_for_start(screen, trigger_handler, config):
            print("Task cancelled before start.")
            return False
        
        print("Task started!")
        start_time = time.perf_counter()
        task_start_timestamp = datetime.now()
        
        # Log initial timestamp for clinical research verification
        print(f"Task start timestamp: {task_start_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        
        # Show instruction screen during dummy scans/discarded acquisitions
        if instruction_image:
            print(f"\n--- Instruction Screen (Dummy Scans) ---")
            instruction_start = time.perf_counter()
            instruction_timestamp = datetime.now()
            print(f"  Instruction start timestamp: {instruction_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            print(f"  Displaying instruction screen for {instruction_duration}s...")
            if not show_instruction_image(screen, instruction_image, instruction_duration):
                print("Task cancelled during instruction screen.")
                return False
            instruction_actual = time.perf_counter() - instruction_start
            print(f"  Instruction screen completed (actual: {instruction_actual:.3f}s, expected: {instruction_duration:.1f}s)")
        
        # Run 5 cycles
        for cycle in range(1, NUM_CYCLES + 1):
            print(f"\n--- Cycle {cycle} of {NUM_CYCLES} ---")
            cycle_start = time.perf_counter()
            cycle_timestamp = datetime.now()
            print(f"  Cycle {cycle} start timestamp: {cycle_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            
            # Fixation phase (20 seconds)
            print(f"  Fixation phase ({FIXATION_DURATION}s)...")
            fixation_start = time.perf_counter()
            if not show_fixation(screen, fixation_image, FIXATION_DURATION):
                print("Task cancelled during fixation.")
                return False
            fixation_actual = time.perf_counter() - fixation_start
            print(f"    Fixation completed (actual: {fixation_actual:.3f}s, expected: {FIXATION_DURATION:.1f}s)")
            
            # Checkerboard phase (20 seconds, 8 Hz flashing)
            print(f"  Checkerboard phase ({CHECKERBOARD_DURATION}s, {FLASH_FREQUENCY} Hz)...")
            checkerboard_start = time.perf_counter()
            if not show_flashing_checkerboard(screen, checkerboard1, checkerboard2, 
                                            CHECKERBOARD_DURATION, FLASH_FREQUENCY):
                print("Task cancelled during checkerboard.")
                return False
            checkerboard_actual = time.perf_counter() - checkerboard_start
            print(f"    Checkerboard completed (actual: {checkerboard_actual:.3f}s, expected: {CHECKERBOARD_DURATION:.1f}s)")
            
            cycle_duration = time.perf_counter() - cycle_start
            print(f"  Cycle {cycle} completed in {cycle_duration:.2f}s (expected: {FIXATION_DURATION + CHECKERBOARD_DURATION:.1f}s)")
        
        total_duration = time.perf_counter() - start_time
        expected_duration = NUM_CYCLES * (FIXATION_DURATION + CHECKERBOARD_DURATION) + instruction_duration
        task_end_timestamp = datetime.now()
        timing_drift = total_duration - expected_duration
        
        print(f"\n{'=' * 60}")
        print(f"Task completed successfully!")
        print(f"Task end timestamp: {task_end_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print(f"Total duration: {total_duration:.3f}s")
        print(f"Expected duration: {expected_duration:.1f}s")
        if abs(timing_drift) > 0.1:  # Warn if drift > 100ms
            print(f"WARNING: Timing drift detected: {timing_drift:.3f}s")
        else:
            print(f"Timing accuracy: {abs(timing_drift):.3f}s drift (within acceptable range)")
        print(f"{'=' * 60}\n")
        
        # Show completion message
        show_message(screen, "Task Complete!\n\nThank you.\n\nWindow will close in 3 seconds...",
                    wait_for_input=False, escape_cancels=False)
        time.sleep(3)
        
        return True
        
    except KeyboardInterrupt:
        print("\nTask interrupted by user.")
        return False
    finally:
        if trigger_handler:
            trigger_handler.stop()


# --- Main Application ---
def main():
    """Main application entry point."""
    print("fMRI Visual Task Application")
    print(f"Version: {APP_VERSION}")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    print(f"Configuration loaded.")
    print(f"  Color scheme: {config.get('color_scheme', 'blue_yellow')}")
    print(f"  Trigger character: '{config['trigger_character']}'")
    print(f"  Start mode: {config.get('start_mode', 'both')}")
    fixation_display = config.get('fixation_image') if config.get('fixation_image') else 'rendered programmatically'
    print(f"  Fixation: {fixation_display}")
    print(f"  Checkerboard images: {config['checkerboard_image1']}, {config['checkerboard_image2']}")
    
    # Initialize Pygame
    try:
        pygame.init()
        if not pygame.font:
            pygame.font.init()
        
        # Get screen info
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        
        # Create fullscreen display
        flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        try:
            screen = pygame.display.set_mode((screen_width, screen_height), flags)
        except pygame.error:
            flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
            screen = pygame.display.set_mode((screen_width, screen_height), flags)
        
        actual_width, actual_height = screen.get_size()
        pygame.display.set_caption("fMRI Visual Task")
        pygame.mouse.set_visible(False)
        
        print(f"Display initialized: {actual_width}x{actual_height}")
        
    except pygame.error as e:
        print(f"ERROR: Failed to initialize Pygame: {e}")
        print("Please ensure your display is properly configured.")
        return 1
    
    # Run the task
    try:
        success = run_task(screen, config)
        return 0 if success else 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        pygame.quit()
        print("Application closed.")


if __name__ == '__main__':
    sys.exit(main())

