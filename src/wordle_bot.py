from time import sleep
from pynput.keyboard import Controller, Key
from pydantic import BaseModel
from src.prompts import SYSTEM_PROMPT

from langchain_core.messages import HumanMessage, ToolMessage
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()


class WordleGuess(BaseModel):
    guess: str
    solved: bool


class WordleBot:
    
    def __init__(self, model=ChatGoogleGenerativeAI, model_name="gemini-2.5-flash", temperature=0.5):
        self.llm = model(model=model_name, temperature=temperature)
        self.agent = create_agent(
                        model=self.llm, 
                        tools=[self.type_word],
                        middleware=[self.handle_tool_errors], 
                        system_prompt=SYSTEM_PROMPT,
                        response_format=ToolStrategy(WordleGuess)
                        )
        self.response: str = ""
    
    @staticmethod
    def create_message(image_data):
        input_message = [
                {"type": "text", "text": "Here's the wordle puzzle so far. Make a guess."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_data}"},
                }
            ]
        
        return HumanMessage(content=input_message)
    
    def invoke(self, image_data):
        message = self.create_message(image_data)
        response = None
        
        # Streaming
        for chunk in self.agent.stream(
            {"messages": message},
            stream_mode="updates"
        ):
            for step, data in chunk.items():
                print(f"[LOG] Step: {step}")
                content_blocks = data['messages'][-1].content_blocks
                if content_blocks[-1]["type"] == "text":
                    print(f"[LOG] Content: {content_blocks[-1]["text"]}")
                else:
                    print(f"[LOG] Content: {content_blocks}")
                response = data.get("structured_response", None)
        
        return response
            
    @staticmethod
    @tool("type_word", description="Type a word in the current open window.")
    def type_word(word: str, delay: float = 0.4):
        """Type the word using the keyboard"""
        kb = Controller()
        sleep(1)
        for char in word:
            kb.type(char)
            sleep(delay)
        sleep(0.5)
        kb.press(Key.enter)
        sleep(0.5)
        kb.press(Key.enter)
    
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
            
    def get_token_metadata(self):
        input_tokens, output_tokens, total_tokens = 0
        
        for msg in self.reponse["messages"]:
            if msg["type"] == "AIMessage":
                token_usage = msg["metadata"]["usage"]
                input_tokens += token_usage["input_tokens"]
                output_tokens += token_usage["output_tokens"]
                total_tokens += token_usage["total_tokens"]
                
        return {
            "Input Tokens": input_tokens,
            "Output Tokens": output_tokens,
            "Total Tokens": total_tokens
        }