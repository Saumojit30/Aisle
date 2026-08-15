import logging
from langchain_core.language_models.chat_models import BaseChatModel
from app.config import settings

logger = logging.getLogger(__name__)

def get_llm(model_name: str, temperature: float = 0.0) -> BaseChatModel:
    """Factory to return either ChatGoogleGenerativeAI or ChatGroq based on the model name."""
    is_gemini = "gemini" in model_name.lower()
    
    if is_gemini:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = settings.gemini_api_key or None
            logger.info("Initializing Gemini model: %s (temp: %s)", model_name, temperature)
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=api_key,
            )
        except Exception as e:
            logger.exception("Failed to initialize ChatGoogleGenerativeAI, falling back to basic mock behavior: %s", str(e))
            raise e
    else:
        try:
            from langchain_groq import ChatGroq
            api_key = settings.groq_api_key or None
            logger.info("Initializing Groq model: %s (temp: %s)", model_name, temperature)
            return ChatGroq(
                model=model_name,
                temperature=temperature,
                groq_api_key=api_key,
            )
        except Exception as e:
            logger.exception("Failed to initialize ChatGroq, falling back: %s", str(e))
            raise e
