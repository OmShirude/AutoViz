import logging
import requests
import json
from django.conf import settings

# This will integrate with Django's logging configuration.
logger = logging.getLogger(__name__)

class LLMHandler:
    """
    Handles communication with a local Ollama instance, structured for use
    within a Django application.

    This class is designed to request and receive structured JSON output
    from the LLM, making it suitable for predictable, data-driven tasks.
    """

    def __init__(self):
        """
        Initializes the handler by pulling configuration from Django's settings.
        This allows for easy environment management (e.g., dev vs. prod).
        """
        # Get the Ollama API URL from settings, with a fallback for local dev
        self.api_url = getattr(settings, 'OLLAMA_BASE_URL', "http://localhost:11434/api/generate")
        
        # Get the model name from settings, defaulting to "mistral"
        self.model_name = getattr(settings, 'OLLAMA_MODEL_NAME', "mistral")

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends prompts to the Ollama LLM and returns the raw JSON string response.

        Note: This function returns a string that is expected to be JSON,
        not a parsed Python dictionary. The calling code is responsible for
        parsing this string using json.loads().

        :param system_prompt: The system prompt to guide the model's behavior,
                              persona, and output format.
        :param user_prompt: The user's specific query or input.
        :return: A string containing the LLM's JSON-formatted response,
                 or an empty string "" if an error occurs.
        """
        # Combine system and user prompts for the Ollama /api/generate endpoint
        full_prompt = f"{system_prompt}\n\nUser Query: {user_prompt}"

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            # This key is crucial: it instructs Ollama to ensure its output is valid JSON.
            "format": "json" 
        }

        try:
            # It's good practice to set a timeout for network requests.
            # 60 seconds is a reasonable starting point for local models.
            response = requests.post(self.api_url, json=payload, timeout=60)
            
            # This will raise an HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status()

            response_data = response.json()
            
            # When using format: "json", the model's output is a string inside
            # the 'response' key of the main response object.
            # We return this string directly.
            json_string_content = response_data.get("response", "")
            return json_string_content.strip()

        except requests.exceptions.Timeout:
            logger.error(f"Ollama API call timed out after 60 seconds.", exc_info=True)
            return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}", exc_info=True)
            return ""
        except json.JSONDecodeError as e:
            # This error would happen if the initial response from Ollama itself isn't JSON
            logger.error(f"Failed to decode the primary response from Ollama: {e}", exc_info=True)
            return ""
        except Exception as e:
            logger.error(f"An unexpected error occurred in LLMHandler: {e}", exc_info=True)
            return ""