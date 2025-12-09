from time import sleep
from pynput import keyboard
from pydantic import BaseModel
from src.prompts import AGENT_PROMPT, ANALYZER_PROMPT

from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()


class WordleGuess(BaseModel):
    guess: str
    analysis: str
    solved: bool


class WordleBot:
    
    def __init__(self, model=ChatGoogleGenerativeAI, model_name="gemini-2.5-flash", temperature=0.5):
        self.llm = model(model=model_name, temperature=temperature)
        self.agent = create_agent(
                        model=self.llm, 
                        tools=[self.type_word, self.clear_entry],
                        middleware=[self.handle_tool_errors], 
                        system_prompt=AGENT_PROMPT,
                        response_format=ToolStrategy(WordleGuess)
                        )
    
    @staticmethod
    def create_message(image_data: str):
        input_message = [
                {"type": "text", "text": "Wordle Puzzle Image:"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_data}"},
                }
            ]
        return HumanMessage(content=input_message)
    
    def invoke(self, image_data: str):
        message = self.create_message(image_data)
        print(f"[INFO] Analyzing puzzle...")
        rules = self.analyze_puzzle(message)
        
        # Streaming
        for chunk in self.agent.stream(
            {"messages": HumanMessage(content=rules)},
            stream_mode="updates"
        ):
            for step, data in chunk.items():
                content_blocks = data['messages'][-1].content_blocks
                if step == "tools":
                    print(f"[LOG] {content_blocks[-1]["text"]}")
                response = data.get("structured_response", None)
        return response
            
    @staticmethod
    @tool("type_word", description="Type a word in the current open window.")
    def type_word(word: str, delay: float = 0.3):
        """Type the word using the keyboard"""
        kb = keyboard.Controller()
        for char in word:
            kb.type(char)
            sleep(delay)
        kb.type("\n")
        return "Word typed successfully."

    @staticmethod
    @tool("clear_entry", description="Clear the current invalid entry in the puzzle.")
    def clear_entry(delay: float = 0.1):
        """Clear the current entry by pressing backspace on the keyboard 5 times"""
        print("[LOG] Invalid word found.")
        kb = keyboard.Controller()
        for _ in range(5):
            kb.press(keyboard.Key.backspace)
            kb.release(keyboard.Key.backspace)
            sleep(delay)
        return "Invalid entry cleared."
        
    def analyze_puzzle(self, image_data: HumanMessage):
        """Look for clues in the previous guess in the image"""
        input_msg = [{"type": "text", "text": ANALYZER_PROMPT}]
        input_prompt = SystemMessage(content=input_msg)
        response = self.llm.invoke([input_prompt, image_data])
        print(f"[LOG] {response.content}")
        return response.content
    
    @staticmethod
    @wrap_tool_call
    def handle_tool_errors(request, handler):
        """Handle tool execution errors with custom messages."""
        try:
            return handler(request)
        except Exception as e:
            # Return a custom error message to the model
            return ToolMessage(
                content=f"Tool error: Please check your input and try again. ({str(e)})",
                tool_call_id=request.tool_call["id"]
            )