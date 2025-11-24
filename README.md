# Wordle Bot

This project implements an AI-powered Wordle bot that can play the popular word-guessing game "Wordle" by interacting directly with the screen. The bot utilizes a large language model (LLM) to make intelligent guesses based on the visual state of the game, simulates keyboard input to enter its guesses, and incorporates screen capture for real-time game analysis.

## Features

-   **LLM-Powered Guessing:** Integrates with Google's `gemini-2.5-flash` model via `langchain-google-genai` to generate strategic Wordle guesses.
-   **Screen Capture:** Captures the Wordle game board directly from your screen using `pyautogui`.
-   **User Calibration:** Allows the user to calibrate the game area on their screen, ensuring accurate screenshot capture.
-   **Input Simulation:** Simulates keyboard presses using `pynput` to type guesses into the Wordle game.
-   **Strategic Play:** Follows predefined strategies, such as starting with vowel-rich words and using tile color feedback (green, yellow, gray) to refine subsequent guesses.
-   **Structured Output:** Employs Pydantic models to ensure the LLM's responses (guesses and solved status) are well-structured and reliable.

## How it Works

The Wordle Bot operates through the following steps:

1.  **Screen Calibration:** The user first calibrates the bot by defining the top-left and bottom-right corners of the Wordle game area on their screen.
2.  **Screenshot Capture:** The bot takes a screenshot of the defined game area.
3.  **Visual Analysis (LLM Input):** The screenshot is converted into a base64 encoded image and sent to the `gemini-2.5-flash` LLM along with a system prompt outlining the rules of Wordle, the bot's role, and strategic instructions.
4.  **Intelligent Guessing:** The LLM processes the image and the prompt to determine the best possible five-letter word to guess or identifies if the puzzle is already solved.
5.  **Input Simulation:** If a guess is made, the bot uses `pynput` to simulate typing the word into the Wordle game and pressing Enter.
6.  **Iteration:** The process repeats for up to six attempts until the word is guessed or the attempts run out.

## Setup and Installation

### Prerequisites

-   Python 3.13 or higher
-   An active internet connection for LLM interaction
-   Google API Key with access to `gemini-2.5-flash`

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/wordle-bot.git
    cd wordle-bot
    ```

2.  **Set up a virtual environment and install dependencies:**
    ```bash
    uv pip install -r requirements.txt # or pip install -r requirements.txt
    ```

3.  **Configure your Google API Key:**
    Create a `.env` file in the root directory of the project and add your Google API key:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY"
    ```
    Replace `"YOUR_API_KEY"` with your actual Google API key.

## Usage

1.  **Run the bot:**
    ```bash
    python main.py
    ```

2.  **Calibrate the screen:**
    Follow the on-screen instructions to move your mouse to the top-left and bottom-right corners of the Wordle game board and press the specified key (default is `[`, configurable in `main.py`).

3.  **Start the game:**
    Once calibrated, navigate to the Wordle game in your browser. The bot will automatically take screenshots and make guesses.

## Configuration

You can adjust some parameters in `main.py`:

-   `PRTSC_KEY`: The key used for screen calibration (default: `[`).
-   `MODEL_NAME`: The specific Google Generative AI model to use (default: `gemini-2.5-flash`).
-   `TEMPERATURE`: The creativity/randomness of the LLM's responses (default: `0.1`).

## TODOs

-   Create a dedicated screenshot analyzer agent to generate constraints for word suggestions.
-   Implement a more robust LangChain chain for complex reasoning.
-   Improve token count tracking for cost optimization.
