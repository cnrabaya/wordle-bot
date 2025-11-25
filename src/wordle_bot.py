from time import sleep
from pynput import keyboard
from pydantic import BaseModel
from src.prompts import AGENT_PROMPT, ANALYZER_PROMPT

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
    analysis: str
    solved: bool


class WordleBot:
    
    def __init__(self, model=ChatGoogleGenerativeAI, model_name="gemini-2.5-flash", temperature=0.5):
        self.llm = model(model=model_name, temperature=temperature)
        self.agent = create_agent(
                        model=self.llm, 
                        tools=[self.type_word, self.analyze_puzzle],
                        middleware=[self.handle_tool_errors], 
                        system_prompt=AGENT_PROMPT,
                        response_format=ToolStrategy(WordleGuess)
                        )
        self.tokens = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                    }
    
    @staticmethod
    def create_message(image_data: str):
        input_message = [
                {"type": "text", "text": "Here's the Wordle puzzle so far."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_data}"},
                }
            ]
        
        return HumanMessage(content=input_message)
    
    def invoke(self, image_data: str):
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
                elif step == "model":
                    print(f"[LOG] Content: {content_blocks}")
                response = data.get("structured_response", None)
        
        return response
            
    @staticmethod
    @tool("type_word", description="Type a word in the current open window.")
    def type_word(word: str, delay: float = 0.3):
        """Type the word using the keyboard"""
        kb = keyboard.Controller()
        sleep(1)
        for char in word:
            kb.type(char)
            sleep(delay)
        kb.type("\n")
        return "Word typed successfully"
        
    @tool("analyze_puzzle", description="Analyze the current wordle puzzle state for clues.")
    def analyze_puzzle(self, image_data: str):
        img_prompt = self.create_message(image_data)
        input_msg = [{"type": "text", "text": ANALYZER_PROMPT}]
        input_prompt = HumanMessage(content=input_msg)
        response = self.llm.invoke({"messages": [input_prompt, img_prompt]})
        return response["messages"][-1].content
    
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