import json
import os

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI


load_dotenv()


DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"
DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"


def generate_json(
    system_prompt: str,
    user_prompt: str,
    groq_model: str = DEFAULT_GROQ_MODEL,
    openai_model: str = DEFAULT_OPENAI_MODEL,
) -> dict:
    """
    Generate structured JSON.

    Groq is the primary provider.
    OpenAI is used as a fallback if Groq fails.
    """

    groq_key = os.getenv(
        "GROQ_API_KEY"
    )

    openai_key = os.getenv(
        "OPENAI_API_KEY"
    )

    last_error = None

    # -------------------------------------------------
    # 1. Groq
    # -------------------------------------------------

    if groq_key:

        try:

            client = Groq(
                api_key=groq_key
            )

            request_args = {
                "model": groq_model,

                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],

                "response_format": {
                    "type": "json_object"
                },

                "temperature": 0,

                "max_completion_tokens": 4096,
            }

            # GPT-OSS models support explicit reasoning
            # effort control.
            if groq_model in {
                "openai/gpt-oss-20b",
                "openai/gpt-oss-120b",
            }:
                request_args[
                    "reasoning_effort"
                ] = "low"

            response = client.chat.completions.create(
                **request_args
            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            if not content:
                raise RuntimeError(
                    "Groq returned an empty response."
                )

            return json.loads(content)

        except Exception as error:

            last_error = error

            print(
                f"Groq request failed: {error}"
            )

    # -------------------------------------------------
    # 2. OpenAI fallback
    # -------------------------------------------------

    if openai_key:

        try:

            client = OpenAI(
                api_key=openai_key
            )

            response = client.chat.completions.create(
                model=openai_model,

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],

                response_format={
                    "type": "json_object"
                },

                temperature=0,

                max_tokens=4096,
            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            if not content:
                raise RuntimeError(
                    "OpenAI returned an empty response."
                )

            return json.loads(content)

        except Exception as error:

            last_error = error

            print(
                f"OpenAI fallback failed: {error}"
            )

    raise RuntimeError(
        "No LLM provider succeeded. "
        f"Last error: {last_error}"
    )