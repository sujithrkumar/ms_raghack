# Note: The openai-python library support for Azure OpenAI is in preview.
import logging
import openai
import os
import json

from utils.custom_logging import setup_logging
from openai import AzureOpenAI, AsyncAzureOpenAI
from config import LLM_CONF

setup_logging()
logger = logging.getLogger("project_logger")

os.environ["OPENAI_LOG"] = "debug"


class AzureOpenAILLM:
    def __init__(self, LLM_CONF) -> None:
        self.client = AzureOpenAI(
            api_version="2024-02-15-preview",
            azure_endpoint=LLM_CONF["end_point"],
            api_key=LLM_CONF["api_key"]
        )

    def get_llm_response(self, messages: list):
        """Gets the LLM response for the given prompt. Returns None if an error occurs.

        Args:
            prompt (_type_): Prompt string to be passed to the LLM. Prompt should specify the JSON response to be returned.

        Returns:
            _type_: JSON object incase of success or None incase of an error.
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",  # e.g. gpt-35-instant
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                top_p=0.95,
                max_tokens=4000
            )
            response = completion.model_dump_json(indent=4, exclude_unset=True)
            logger.info(
                f"LLM Response:\n{response}")
            response_content = completion.choices[0].message.content
            logger.debug(f"Response Content: {response_content}")
            if response_content:
                return json.loads(response_content)
            else:
                logger.error("Could not get valid LLM response.")
                return None
        except openai.APIConnectionError as e:
            logger.error(
                "The server could not be reached due to connection error", exc_info=e)
            # an underlying Exception, likely raised within httpx.
            logger.error(e.__cause__)
            return None
        except openai.RateLimitError as e:
            logger.error(
                "A 429 status code was received from LLM; we should back off a bit.", exc_info=e)
            return None
        except openai.APIStatusError as e:
            logger.error(
                "Another non-200-range status code was received with LLM", exc_info=e)
            logger.error(e.status_code)
            logger.error(e.response)
            return None
