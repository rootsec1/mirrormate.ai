import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Local
from constants import GEMINI_API_KEY


class LLMClient():
    model: genai.GenerativeModel = None

    def __init__(self):
        self.__init_gemini_model__()

    def __init_gemini_model__(self) -> genai.GenerativeModel:
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            "models/gemini-pro",
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

    def prompt(self, text: str) -> str:
        return self.model.generate_content(text).text.strip()
