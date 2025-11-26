"""
LLM client using OpenAI compatible API
"""

from typing import List
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with OpenAI compatible LLM APIs"""

    def __init__(
        self,
        api_base: str,
        api_key: str,
        model_name: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize LLM client

        Args:
            api_base: Base URL for the API
            api_key: API key for authentication
            model_name: Name of the model to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.client = OpenAI(
            base_url=api_base,
            api_key=api_key,
            timeout=timeout
        )
        self.model_name = model_name
        self.max_retries = max_retries

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def _call_api(self, messages: List[dict]) -> str:
        """
        Internal method to call API with retry logic

        Args:
            messages: List of message dictionaries

        Returns:
            Response content from the API

        Raises:
            Exception: If API call fails after all retries
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent outputs
                response_format={
        'type': 'json_object'}
            )
            
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise

    def infer_batch(self, prompt: str) -> str:
        """
        Send inference request for a batch of names

        Args:
            prompt: Complete prompt including names to analyze

        Returns:
            Raw response from the LLM

        Raises:
            Exception: If API call fails after all retries
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert in identifying scholars' nationalities and genders based on their names, historical context, and cultural backgrounds."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        logger.info(f"Sending batch inference request to {self.model_name}")
        response = self._call_api(messages)
        logger.info("Batch inference completed successfully")

        return response
