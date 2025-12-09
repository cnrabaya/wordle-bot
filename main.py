from src.wordle_bot import WordleBot
from src.screen_capture import ScreenCapture
from time import sleep
from langchain_google_genai import ChatGoogleGenerativeAI
# Import other model/s here

def main():
    # Define constants
    PRTSC_KEY = "["
    MODEL = ChatGoogleGenerativeAI
    MODEL_NAME = "gemini-2.5-flash"
    TEMPERATURE = 0.0
    
    # Calibrate screen
    prtsc = ScreenCapture(PRTSC_KEY)
    prtsc.calibrate_screen()
    sleep(2)
    
    bot = WordleBot(MODEL, MODEL_NAME, TEMPERATURE)
    while (True):
        # Take screenshot and convert to base64
        screenshot = prtsc.print_screen()
        screenshot_b64 = prtsc.pil_to_base64(screenshot)
        
        print("[INFO] Please move to your browser window.")
        
        response = bot.invoke(screenshot_b64)
        if response.solved is True:
            break
        else:
            print(f"[LOG] GUESS: {response.guess}")
            print(f"[LOG] ANALYSIS: {response.analysis}")
            
        sleep(1)

if __name__ == "__main__":
    main()