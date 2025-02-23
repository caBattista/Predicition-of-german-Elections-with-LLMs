import os
import time
from typing import Any, Optional, Tuple, Type
import logging
from pydantic import BaseModel
from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        temperature: float = 0.7
    ):
    
        # Load environment variables from project root
        project_root = Path(__file__).parent.parent
        load_dotenv(project_root / ".env")
        
        # Get API key from argument or environment
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in arguments or environment")
            
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.temperature = temperature

    def structured_call(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[BaseModel],
        response_format: dict = {"type": "object"},
        max_tokens: int = 4000
    ) -> Tuple[Optional[BaseModel], Optional[str]]:
        for attempt in range(self.max_retries):
            try:
                # Make the API call
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format=response_format,
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                
                # Extract and parse the response
                response_text = completion.choices[0].message.content
                if not response_text:
                    raise ValueError("Empty response from API")
                
                # Parse and validate with Pydantic
                try:
                    # First try to parse as JSON
                    response_json = json.loads(response_text)
                    # Then validate with Pydantic
                    #parsed_response = response_model.model_validate(response_json)
                    return response_json, None
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON: {str(e)}")
                    if attempt == self.max_retries - 1:
                        return None, f"Failed to parse JSON: {str(e)}"
                    continue
                except Exception as e:
                    logger.warning(f"Failed to validate response: {str(e)}")
                    if attempt == self.max_retries - 1:
                        return None, f"Failed to validate response: {str(e)}"
                    continue

            except Exception as e:
                error_msg = f"API call failed: {str(e)}"
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries}: {error_msg}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                return None, error_msg

        return None, "Max retries exceeded"

def get_default_client() -> OpenAIClient:
    # Load environment variables again to ensure they're available
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable not set. "
            "Please set it in .env file or environment"
        )
    
    return OpenAIClient(api_key=api_key)