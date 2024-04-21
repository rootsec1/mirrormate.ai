import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Local
from constants import GEMINI_API_KEY

class LLMClient():
    """
    A client for interacting with the Gemini Pro generative model from Google's GenerativeAI.
    """

    model: genai.GenerativeModel = None  # The generative model

    def __init__(self):
        """
        Initialize the LLMClient and the generative model.
        """
        self.__init_gemini_model__()

    def __init_gemini_model__(self) -> genai.GenerativeModel:
        """
        Initialize the Gemini Pro generative model with the provided API key and safety settings.
        """
        # Configure the GenerativeAI with the API key
        genai.configure(api_key=GEMINI_API_KEY)
        # Initialize the generative model with the model path and safety settings
        self.model = genai.GenerativeModel(
            "models/gemini-pro",
            safety_settings={
                # Set the harm block thresholds for hate speech and harassment to none
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

    def prompt(self, text: str) -> str:
        """
        Generate content using the Gemini Pro model given a prompt text.
        """
        # Generate content using the model and return the text, stripped of leading/trailing whitespace
        return self.model.generate_content(text).text.strip()