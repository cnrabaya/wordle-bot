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
    TEMPERATURE = 0.1
    
    # Calibrate screen
    prtsc = ScreenCapture(PRTSC_KEY)
    prtsc.calibrate_screen()
    
    bot = WordleBot(MODEL, MODEL_NAME, TEMPERATURE)
    attempts = 0
    
    while attempts < 6:
        attempts += 1    
        # Take screenshot and convert to base64
        screenshot = prtsc.print_screen()
        screenshot_b64 = prtsc.pil_to_base64(screenshot)
        
        print("[INFO] Please move to your browser window.")
        sleep(3)
        print(f"[INFO] Taking a guess...")
        
        response = bot.invoke(screenshot_b64)
        if response.solved is True:
            break
        else:
            print(f"[LOG] GUESS#{attempts}: {response.guess}")
        
        sleep(1)

if __name__ == "__main__":
    main()

# TODO: 
# 1. Create screenshot analyzer agent, generates constraints for word
# 2. LangChain chain
# 3. Implement token count
# 4. Implement screenshot check using matplotlib