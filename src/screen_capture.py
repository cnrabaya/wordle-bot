from pynput import keyboard
from io import BytesIO
from PIL import Image
import pyautogui
import base64

class ScreenCapture:
    
    def __init__(self, key: str = "p"):
        self.key = key
        self.coords = {}
        
    @staticmethod
    def pil_to_base64(image: Image) -> str:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64_str = base64.b64encode(buffered.getvalue()).decode()

        return img_base64_str
    
    def on_press(self, key):
        try:
            if key.char == self.key:
                x, y = pyautogui.position()
                print(f"[LOG] X: {x}, Y: {y}")
                if not self.coords:
                    self.coords["top_left"] = (x, y)
                else:
                    self.coords["bottom_right"] = (x, y)
                return False
        except AttributeError as e:
            print(f"[WARNING] : {e}")
    
    def calibrate_screen(self):
        regions = ["top_left", "bottom_right"]
        for region in regions:
            print(f"[INFO] Move the mouse to the {region} region and press '{self.key}'.")
            with keyboard.Listener(on_press=self.on_press) as keyboard_listener:
                keyboard_listener.join(timeout=40)
                
        self.coords["width"] = self.coords["bottom_right"][0] - self.coords["top_left"][0]
        self.coords["height"] = self.coords["bottom_right"][1] - self.coords["top_left"][1]
        
        print("[INFO] Screen calibrated!")
    
    def print_screen(self):        
        screen_xywh = (
            self.coords["top_left"][0], # x-coord
            self.coords["top_left"][1], # y-coord
            self.coords["width"],       # width
            self.coords["height"]       # height
        )
        
        screenshot = pyautogui.screenshot(region=screen_xywh)
        print("[INFO] Screenshot taken!")
        return screenshot