"""
Translation service.
"""

from deep_translator import GoogleTranslator
from backend.utils.exceptions import TranslationError

__all__ = ["translate_text", "detect_and_translate"]


def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Translate text to the target language.
    
    Args:
        text (str): The text to translate.
        target_lang (str): The target language code. Defaults to "en".
        
    Returns:
        str: The translated text.
        
    Raises:
        TranslationError: If translation fails.
    """
    try:
        translator = GoogleTranslator(source="auto", target=target_lang)
        return translator.translate(text)
    except Exception as e:
        raise TranslationError(f"Translation failed: {e}")


def detect_and_translate(text: str) -> tuple[str, str]:
    """
    Detect language and return English translation + original language code.
    
    Args:
        text (str): The text to detect and translate.
        
    Returns:
        tuple[str, str]: A tuple containing the English translation and the detected language code.
        
    Raises:
        TranslationError: If detection or translation fails.
    """
    try:
        # Note: deep_translator's GoogleTranslator auto-detects but does not easily expose 
        # the detected language code in the simple API.
        # We will assume 'auto' as the source and translate to English.
        translator = GoogleTranslator(source="auto", target="en")
        translation = translator.translate(text)
        detected_lang = "auto"
        return translation, detected_lang
    except Exception as e:
        raise TranslationError(f"Detection and translation failed: {e}")
