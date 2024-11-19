
import os
import time
import random
import math
import cv2
import keyboard
import mss
import numpy as np
import pygetwindow as gw
import win32api
import win32con
import warnings
import pyfiglet
from pywinauto import Application

# Watermark: https://t.me/mizegerddev & https://github.com/mizegerd-tech

# Interval in seconds to check for play button
CHECK_INTERVAL = 5

# Suppress specific warnings from pywinauto
warnings.filterwarnings("ignore", category=UserWarning, module='pywinauto')

def list_windows_by_title(title_keywords):
    """
    List all windows that contain any of the specified keywords in their title.
    
    Args:
        title_keywords (list): List of keywords to search for in window titles.
    
    Returns:
        list: List of tuples containing window title and handle.
    """
    windows = gw.getAllWindows()
    filtered_windows = []
    for window in windows:
        for keyword in title_keywords:
            if keyword.lower() in window.title.lower():
                filtered_windows.append((window.title, window._hWnd))
                break
    return filtered_windows

class Logger:
    """
    Simple logger class to print messages with an optional prefix.
    """
    def __init__(self, prefix=None):
        self.prefix = prefix

    def log(self, data: str):
        """
        Log a message with the optional prefix.
        
        Args:
            data (str): Message to log.
        """
        if self.prefix:
            print(f"{self.prefix} {data}")
        else:
            print(data)

class AutoClicker:
    """
    AutoClicker class to automate clicking on specific colors in a window.
    """
    def __init__(self, hwnd, target_colors_hex, nearby_colors_hex, threshold, logger, target_percentage, collect_freeze):
        self.hwnd = hwnd
        self.target_colors_hex = target_colors_hex
        self.nearby_colors_hex = nearby_colors_hex
        self.threshold = threshold
        self.logger = logger
        self.target_percentage = target_percentage
        self.collect_freeze = collect_freeze
        self.running = False
        self.clicked_points = []
        self.iteration_count = 0
        self.last_check_time = time.time()
        self.last_freeze_check_time = time.time()
        self.freeze_cooldown_time = 0

    @staticmethod
    def hex_to_hsv(hex_color):
        """
        Convert a hex color to HSV format.
        
        Args:
            hex_color (str): Hex color found, False otherwise.
        """
        x, y = center
        height, width = hsv_img.shape[:2]
        for i in range(max(0, x - radius), min(width, x + radius + 1)):
            for j in range(max(0, y - radius), min(height, y + radius + 1)):
                distance = math.sqrt((x - i) ** 2 + (y - j) ** 2)
                if distance <= radius:
                    pixel_hsv = hsv_img[j, i]
                    for target_hsv in target_hsvs:
                        if np.allclose(pixel_hsv, target_hsv, atol=[1, 50, 50]):
                            return True
        return False

    def check_and_click_play_button(self, sct, monitor):
        """
        Check for the play button and click it if found.
        
        Args:
            sct (mss.mss): MSS screenshot object.
            monitor (dict): Monitor dimensions.
        """
        current_time = time.time()
        if current_time - self.last_check_time >= CHECK_INTERVAL:
            self.last_check_time = current_time
            templates = [
                cv2.imread(os.path.join("template_png", "template_play_button.png"), cv2.IMREAD_GRAYSCALE),
                cv2.imread(os.path.join("template_png", "template_play_button1.png"), cv2.IMREAD_GRAYSCALE),
                cv2.imread(os.path.join("template_png", "close_button.png"), cv2.IMREAD_GRAYSCALE),
                cv2.imread(os.path.join("template_png", "captcha.png"), cv2.IMREAD_GRAYSCALE)
            ]

            for template in templates:
                if template is None:
                    self.logger.log("The template file could not be loaded.")
                    continue

                template_height, template_width = template.shape

                img = np.array(sct.grab(monitor))
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

                res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(res >= self.threshold)

                matched_points = list(zip(*loc[::-1]))

                if matched_points:
                    pt_x, pt_y = matched_points[0]
                    cX = pt_x + template_width // 2 + monitor["left"]
                    cY = pt_y + template_height // 2 + monitor["top"]

                    self.click_at(cX, cY)
                    self.logger.log(f'Button clicked: {cX} {cY}')
                    self.clicked_points.append((cX, cY))
                    break 

    def click_color_areas(self):
        """
        Main loop to click on target color areas in the window.
        """
        app = Application().connect(handle=self.hwnd)
        window = app.window(handle=self.hwnd)
        window.set_focus()

        target_hsvs = [self.hex_to_hsv(color) for color in self.target_colors_hex]
        nearby_hsvs = [self.hex_to_hsv(color) for color in self.nearby_colors_hex]

        with mss.mss() as sct:
            keyboard.add_hotkey('F6', self.toggle_script)

            while True:
                if self.running:
                    rect = window.rectangle()
                    monitor = {
                        "top": rect.top,
                        "left": rect.left,
                        "width": rect.width(),
                        "height": rect.height()
                    }
                    img = np.array(sct.grab(monitor))
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

                    for target_hsv in target_hsvs:
                        lower_bound = np.array([max(0, target_hsv[0] - 1), 30, 30])
                        upper_bound = np.array([min(179, target_hsv[0] + 1), 255, 255])
                        mask = cv2.inRange(hsv, lower_bound, upper_bound)
                        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                        num_contours = len(contours)
                        num_to_click = int(num_contours * self.target_percentage)
                        contours_to_click = random.sample(contours, num_to_click)

                        for contour in reversed(contours_to_click):
                            if cv2.contourArea(contour) < 6:
                                continue

                            M = cv2.moments(contour)
                            if M["m00"] == 0:
                                continue
                            cX = int(M["m10"] / M["m00"]) + monitor["left"]
                            cY = int(M["m01"] / M["m00"]) + monitor["top"]

                            if not self.is_near_color(hsv, (cX - monitor["left"], cY - monitor["top"]), nearby_hsvs):
                                continue

                            if any(math.sqrt((cX - px) ** 2 + (cY - py) ** 2) < 35 for px, py in self.clicked_points):
                                continue
                            cY += 5
                            self.click_at(cX, cY)
                            self.logger.log(f'Clicked: {cX} {cY}')
                            self.clicked_points.append((cX, cY))

                    if self.collect_freeze:
                        self.check_and_click_freeze_button(sct, monitor)
                    self.check_and_click_play_button(sct, monitor)
                    time.sleep(0.1)
                    self.iteration_count += 1
                    if self.iteration_count >= 5:
                        self.clicked_points.clear()
                        self.iteration_count = 0

    def check_and_click_freeze_button(self, sct, monitor):
        """
        Check for the freeze button and click it if found.
        
        Args:
            sct (mss.mss): MSS screenshot object.
            monitor (dict): Monitor dimensions.
        """
        freeze_colors_hex = ["#82dce9", "#55ccdc"] 
        freeze_hsvs = [self.hex_to_hsv(color) for color in freeze_colors_hex]
        current_time = time.time()
        if current_time - self.last_freeze_check_time >= 1 and current_time >= self.freeze_cooldown_time:
            self.last_freeze_check_time = current_time
            img = np.array(sct.grab(monitor))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            for freeze_hsv in freeze_hsvs:
                lower_bound = np.array([max(0, freeze_hsv[0] - 1), 30, 30])
                upper_bound = np.array([min(179, freeze_hsv[0] + 1), 255, 255])
                mask = cv2.inRange(hsv, lower_bound, upper_bound)
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    if cv2.contourArea(contour) < 3:
                        continue

                    M = cv2.moments(contour)
                    if M["m00"] == 0:
                        continue
                    cX = int(M["m10"] / M["m00"]) + monitor["left"]
                    cY = int(M["m01"] / M["m00"]) + monitor["top"]

                    self.click_at(cX, cY)
                    self.logger.log(f'Clicked freeze: {cX} {cY}')
                    self.freeze_cooldown_time = time.time() + 4  
                    return 

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    keywords = ["Blum", "Telegram"]
    windows = list_windows_by_title(keywords)
    print("""
                                                                                                       
                                   ███   ██                 ██   ███                                   
                                   ██    ███      ███      ███    ██                                   
                                   ██     ██    ███████    ███    ██                                   
                                   ███    ██   ████ ████   ███    ██                                   
                                   ███    ██   ██     ██   ███    ██                                   
                                   ███   ███   ██     ██   ███   ███                                   
                                   ███   ███   ██     ██   ███   ███                                   
                                   ███   ███   ██     ██   ███   ███                                   
                        ██████████████    ███████     ████████    █████████████                        
                        █████████████     ███████     ███████     ██████████████                       
                       ███                                                   ███                       
                   ██████    █████████████████████████████████████████████    ██████                   
                  ██████    ███████████████████████████████████████████████    ██████                  
                 ████     █████                                         █████     ████                 
                 ██     █████               ███         ███               █████     ██                 
                 ██    █████              ███████     ███████              █████    ██                 
                 ██    ███                ███████     ████████               ███    ██                 
                 ██    ███               ███   ██     ██   ███               ███    ██                 
 ██████████████████    ███          ████████   █████████   ████              ███    ██████████████████ 
 ██████████████████    ███         ████████    █████████   ██████            ███    ██████████████████ 
 █                     ███         ███                       ██████          ███                     █ 
 ██████████████████    ███         ████████     ████████████    ███          ███    ██████████████████ 
 ██████████████████    ███          ████████   ██████████████    ███         ███    ██████████████████ 
                 ██    ███               ███   ███         ██    ███         ███    ██                 
       ████████████    ███               ███   ███████████████   ███         ███    ████████████       
     ██████████████    ███               ███   ██████████████   ████         ███    ██████████████     
     ████              ███               ███                    ███          ███              ████     
     ███               ███               ███                    ███          ███               ███     
     ██████████████    ███               ███    █████████████   ████         ███    ██████████████     
       ████████████    ███               ███   ███████████████   ███         ███    ████████████       
                 ███   ███               ███   ███        ████   ███         ███    ██                 
 ██████████████████    ███          ████████   ██████████████    ███         ███    ██████████████████ 
 ██████████████████    ███         ████████    ██████████████   ███          ███    ██████████████████ 
 █                     ███         ███                       ██████          ███                     █ 
 ██████████████████    ███         ████████     ████████   ███████           ███    ██████████████████ 
 ██████████████████    ███          ████████   █████████   ████              ███    ██████████████████ 
                 ██    ███               ███   ███   ███   ███               ███    ██                 
                 ██    ███               █████████   █████████               ███    ██                 
                 ██    █████              ███████     ███████              █████    ██                 
                 ███   ███████              ███         ███              ███████    ██                 
                 ████    ████████████████████████████████████████████████████     ████                 
                 ████████  █████████████████████████████████████████████████  ████████                 
                  ████████   █████████████████████████████████████████████    ███████                  
                       ███                                                   ████                      
                       ██████████████     ███████     ███████     ██████████████                       
                        ██████████████   █████████    ████████   ██████████████                        
                                   ███   ███   ███   ███   ███   ███                                   
                                   ███   ███   ███   ███   ███   ███                                   
                                   ███   ███   ███   ███   ███   ███                                   
                                   ███   ███   ███   ███   ███   ███                                   
                                   ███   ███   █████████   ███   ███                                   
                                   ███   ███   █████████   ███   ███                                   
                                   ███   ███     █████     ███   ███                                   
                                   ████ ████               ████ ████                                   
                                                                                                                                                                                                                                                                                                  
""")
    if not windows:
        print("There are no windows containing the specified Blum or Telegram keywords.")
        exit()
    ascii_banner = pyfiglet.figlet_format("Mizegerddev\nauto-blum", font="Rounded")
    print(ascii_banner)
    print("Windows available for selection:")
    for i, (title, hwnd) in enumerate(windows):
        print(f"{i + 1}: {title}")

    choice = int(input("Enter the number of the window in which the Blum bot is open:")) - 1
    if choice < 0 or choice >= len(windows):
        print("Wrong choice.")
        exit()

    hwnd = windows[choice][1]

    while True:
        try:
            target_percentage = input("You can enter a number between 0.01 and 1 to reduce the game error (enter 1 by default):")
            target_percentage = target_percentage.replace(',', '.')
            target_percentage = float(target_percentage)
            if 0 <= target_percentage <= 1:
                break
            else:
                print("Please enter a value between 0.1 and 1.")
        except ValueError:
            print("Wrong format. Please enter a number.")

    while True:
        try:
            collect_freeze = int(input("Ice click? 1 - Yes, 2 - No:"))
            if collect_freeze in [1, 2]:
                collect_freeze = (collect_freeze == 1)
                break
            else:
                print("Please enter 1 or 2.")
        except ValueError:
            print("Wrong format. Please enter a number.")

    logger = Logger("[https://t.me/Mizegerddev]")
    logger.log("Welcome to the  auto clicker for Blum game.")
    logger.log('After starting the mini-game, press [F6] on your keyboard')
    target_colors_hex = ["#c9e100", "#bae70e"]
    nearby_colors_hex = ["#abff61", "#87ff27"]
    threshold = 0.8  

    auto_clicker = AutoClicker(hwnd, target_colors_hex, nearby_colors_hex, threshold, logger, target_percentage, collect_freeze)
    try:
        auto_clicker.click_color_areas()
    except Exception as e:
        logger.log(f"Something went wrong:")
    for i in reversed(range(5)):
        print(f"The script will exit when:{i}")
        time.sleep(1)
