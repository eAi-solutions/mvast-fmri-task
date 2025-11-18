# -*- coding: utf-8 -*-
"""
fMRI Visual Task - Presentation Computer Application
Compatible with Windows (all versions) and macOS

This program presents visual stimuli for fMRI experiments:
- 5 cycles of alternating fixation (20s) and flashing checkerboard (20s)
- Can be started manually (spacebar) or via scanner trigger signal
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
CONFIG_FILE = "fmri_task_config.json"

# Task Parameters
NUM_CYCLES = 5
FIXATION_DURATION = 20.0  # seconds
CHECKERBOARD_DURATION = 20.0  # seconds
FLASH_FREQUENCY = 8.0  # Hz (8 Hz = 8 flashes per second)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Default configuration
DEFAULT_CONFIG = {
    "trigger_character": "5",  # Common trigger characters: "5", "t", "T", etc.
    "use_serial_port": False,  # Set to True to use serial port for triggers
    "serial_port": None,  # e.g., "COM3" (Windows) or "/dev/ttyUSB0" (Mac/Linux)
    "images_dir": "images",
    "fixation_image": None,  # If None, will render text '+' instead
    "checkerboard_image1": "acheck_by.png",
    "checkerboard_image2": "acheck_by_.png",
    "instruction_image": None,  # Path to instruction image (e.g., "instruction.png")
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
            return merged
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return DEFAULT_CONFIG.copy()
    else:
        # Create default config file
        save_config(DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()


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
            
            ser.close()
        except ImportError:
            print("WARNING: pyserial not installed. Install with: pip install pyserial")
            print("Falling back to keyboard input mode.")
            self._read_keyboard_triggers()
        except Exception as e:
            print(f"Serial port error: {e}. Falling back to keyboard input.")
            self._read_keyboard_triggers()
    
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


def load_fixation_image(screen_width, screen_height, image_path=None):
    """Load fixation plus image, or create a rendered plus sign."""
    if image_path and os.path.exists(image_path):
        try:
            img = pygame.image.load(image_path)
            img = img.convert()
            img = pygame.transform.scale(img, (screen_width, screen_height))
            return img
        except Exception as e:
            print(f"Warning: Could not load fixation image {image_path}: {e}")
    
    # Create a rendered plus sign as fallback
    # Make it large and centered
    surface = pygame.Surface((screen_width, screen_height))
    surface.fill(BLACK)
    
    # Calculate size based on screen dimensions
    cross_size = min(screen_width, screen_height) // 8
    line_width = max(3, cross_size // 20)
    
    center_x, center_y = screen_width // 2, screen_height // 2
    
    # Draw horizontal line
    pygame.draw.rect(surface, WHITE, 
                    (center_x - cross_size // 2, center_y - line_width // 2,
                     cross_size, line_width))
    # Draw vertical line
    pygame.draw.rect(surface, WHITE,
                    (center_x - line_width // 2, center_y - cross_size // 2,
                     line_width, cross_size))
    
    return surface


def load_instruction_image(screen_width, screen_height, image_path=None, instruction_text=None, color_scheme="blue_yellow"):
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
        bg_color = (0, 0, 255)  # BLUE
        text_color = (255, 255, 0)  # YELLOW
    
    surface.fill(bg_color)
    
    # Default instruction text if none provided
    if not instruction_text:
        instruction_text = "Just relax and focus on the center of the screen.\n\nFirst there will be a period of acquisitions with no response.\n\nThen you will see a flashing checker pattern every now and then.\n\nPlease don't look away.\n\nThanks."
    
    # Calculate font size based on screen (larger font for better readability)
    screen_height_px = screen_height
    base_font_size = int(screen_height_px / 15)  # Increased from /18 for even larger text
    font_size = max(42, base_font_size)  # Increased minimum from 36 to 42
    
    try:
        font = pygame.font.Font(None, font_size)
    except:
        font = pygame.font.SysFont("arial", font_size)
    
    # Split text into lines and render (preserve empty lines)
    lines = instruction_text.split('\n')
    rendered_lines = []
    total_height = 0
    
    for line in lines:
        if line:
            rendered = font.render(line, True, text_color)
            rendered_lines.append(rendered)
            total_height += rendered.get_height() + 25  # Increased spacing from 10 to 25
        else:
            rendered_lines.append(None)
            total_height += 35  # Increased spacing from 20 to 35
    
    # Center vertically
    y_start = (screen_height - total_height) // 2
    current_y = y_start
    
    # Draw lines
    for rendered in rendered_lines:
        if rendered:
            rect = rendered.get_rect(centerx=screen_width // 2, top=current_y)
            surface.blit(rendered, rect)
            current_y += rendered.get_height() + 25  # Increased spacing from 10 to 25
        else:
            current_y += 35  # Increased spacing from 20 to 35
    
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
    """Display fixation cross/image for specified duration."""
    if not screen:
        return True
        
    screen.fill(BLACK)
    screen.blit(fixation_image, (0, 0))
    pygame.display.flip()
    
    start_time = time.perf_counter()
    while time.perf_counter() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if escape_cancels and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        time.sleep(0.01)
    
    return True


def show_instruction_image(screen, instruction_image, duration, escape_cancels=True):
    """Display instruction image for specified duration (during dummy scans)."""
    if not screen or not instruction_image:
        return True
    
    screen.fill(BLACK)
    screen.blit(instruction_image, (0, 0))
    pygame.display.flip()
    
    start_time = time.perf_counter()
    while time.perf_counter() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if escape_cancels and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        time.sleep(0.01)
    
    return True


def show_flashing_checkerboard(screen, img1, img2, duration, frequency, escape_cancels=True):
    """Display alternating checkerboard images at specified frequency."""
    if not screen or not img1 or not img2:
        return True
    
    frame_duration = 1.0 / frequency / 2.0  # Half period for each image
    start_time = time.perf_counter()
    end_time = start_time + duration
    current_image = True  # True for img1, False for img2
    last_flip_time = start_time
    
    while time.perf_counter() < end_time:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if escape_cancels and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        # Flip images at the specified frequency
        current_time = time.perf_counter()
        if current_time >= last_flip_time + frame_duration:
            screen.fill(BLACK)
            if current_image:
                screen.blit(img1, (0, 0))
            else:
                screen.blit(img2, (0, 0))
            pygame.display.flip()
            current_image = not current_image
            last_flip_time += frame_duration
        
        # Small sleep to prevent CPU spinning
        time.sleep(0.001)
    
    return True


# --- Wait for Start ---
def wait_for_start(screen, trigger_handler, config, escape_cancels=True):
    """Wait for either spacebar press or trigger signal to start."""
    trigger_char = config.get("trigger_character", "5")
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
    
    # Wait for start signal
    while True:
        # Check keyboard events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("Start signal received: SPACEBAR")
                    return True
                # Check for trigger character key press
                if event.unicode and event.unicode.lower() == trigger_char.lower():
                    print(f"Start signal received: Trigger character '{trigger_char}'")
                    return True
                if escape_cancels and event.key == pygame.K_ESCAPE:
                    return False
        
        # Check for trigger signal from serial port (if configured)
        if trigger_handler and trigger_handler.check_trigger():
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
    fixation_img_path = None
    if config.get("fixation_image"):
        images_dir = resource_path("images")
        fixation_img_path = os.path.join(images_dir, config["fixation_image"])
    
    fixation_image = load_fixation_image(screen_width, screen_height, fixation_img_path)
    
    # Load or create instruction screen (for dummy scans)
    instruction_image = None
    instruction_duration = config.get("instruction_duration", 10.0)
    instruction_text = config.get("instruction_text")
    color_scheme = config.get("color_scheme", "blue_yellow")
    
    # Always create instruction screen (either from image or rendered text)
    # If instruction_image is None, it will render text automatically
    instruction_image = load_instruction_image(
        screen_width, screen_height, 
        config.get("instruction_image"), 
        instruction_text,
        color_scheme
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
    
    if not checkerboard1 or not checkerboard2:
        show_message(screen, "ERROR: Could not load checkerboard images.\n\nPress any key to exit.", 
                   wait_for_input=True, escape_cancels=True)
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
        
        # Show instruction image during dummy scans/discarded acquisitions
        if instruction_image:
            print(f"\n--- Instruction Image (Dummy Scans) ---")
            print(f"  Displaying instruction image for {instruction_duration}s...")
            if not show_instruction_image(screen, instruction_image, instruction_duration):
                print("Task cancelled during instruction image.")
                return False
            print(f"  Instruction image completed.")
        
        # Run 5 cycles
        for cycle in range(1, NUM_CYCLES + 1):
            print(f"\n--- Cycle {cycle} of {NUM_CYCLES} ---")
            
            # Fixation phase (20 seconds)
            print(f"  Fixation phase ({FIXATION_DURATION}s)...")
            cycle_start = time.perf_counter()
            if not show_fixation(screen, fixation_image, FIXATION_DURATION):
                print("Task cancelled during fixation.")
                return False
            
            # Checkerboard phase (20 seconds, 8 Hz flashing)
            print(f"  Checkerboard phase ({CHECKERBOARD_DURATION}s, {FLASH_FREQUENCY} Hz)...")
            if not show_flashing_checkerboard(screen, checkerboard1, checkerboard2, 
                                            CHECKERBOARD_DURATION, FLASH_FREQUENCY):
                print("Task cancelled during checkerboard.")
                return False
            
            cycle_duration = time.perf_counter() - cycle_start
            print(f"  Cycle {cycle} completed in {cycle_duration:.2f}s")
        
        total_duration = time.perf_counter() - start_time
        expected_duration = NUM_CYCLES * (FIXATION_DURATION + CHECKERBOARD_DURATION)
        if instruction_image:
            expected_duration += instruction_duration
        
        print(f"\n{'=' * 60}")
        print(f"Task completed successfully!")
        print(f"Total duration: {total_duration:.2f}s")
        print(f"Expected duration: {expected_duration:.1f}s")
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
    print(f"  Trigger character: '{config['trigger_character']}'")
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

