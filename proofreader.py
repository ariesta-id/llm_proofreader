# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///
"""
GPT-5 Structured Proofreader
============================
A Python script that leverages GPT-5 through the Replicate Structured API 
to proofread text, providing precise corrections, categories, explanations, 
and overall writing feedback.
"""

import os
import time
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from prompts import PROOFREAD_SCHEMA, get_proofread_prompt

# Load environment variables from .env file
load_dotenv()


def proofread_text(
    text: str,
    api_token: Optional[str] = None,
    max_retries: int = 3,
    poll_interval: float = 3.0
) -> Dict[str, Any]:
    """
    Proofreads the given text using GPT-5 via Replicate Structured API.

    Parameters:
        text (str): The text to proofread.
        api_token (str, optional): The Replicate API token. If not provided,
                                   retrieved from the REPLICATE_API_TOKEN env var.
        max_retries (int): Number of retries on API request failures.
        poll_interval (float): Seconds to wait between status checks when polling.

    Returns:
        dict: A dictionary containing 'original_text', 'corrected_text',
              'corrections' (list of detailed changes), and 'overall_feedback'.
    """
    token = api_token or os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        raise ValueError(
            "Replicate API token must be provided or set in the "
            "REPLICATE_API_TOKEN environment variable."
        )

    # 1. Build Payload
    prompt = get_proofread_prompt(text)

    payload = {
        "input": {
            "model": "gpt-5",
            "json_schema": PROOFREAD_SCHEMA,
            "input_item_list": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "enable_web_search": False
        }
    }

    # 2. Setup Headers and Endpoint
    endpoint = "https://api.replicate.com/v1/models/openai/gpt-5-structured/predictions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }

    # 3. Call the API and Poll
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            status = data.get("status")
            poll_url = data.get("urls", {}).get("get")

            # Poll if prediction is asynchronous (starting/processing)
            while status in ["starting", "processing"]:
                time.sleep(poll_interval)
                poll_resp = requests.get(poll_url, headers={"Authorization": f"Bearer {token}"})
                poll_resp.raise_for_status()
                data = poll_resp.json()
                status = data.get("status")

            if status == "succeeded":
                output = data.get("output", {})
                json_output = output.get("json_output")

                # Fallback to parsing 'text' key as JSON if 'json_output' is missing
                if not json_output and "text" in output:
                    try:
                        json_output = json.loads(output["text"])
                    except json.JSONDecodeError:
                        raise ValueError("Failed to parse the model's text output as JSON.")

                if not json_output:
                    raise ValueError("Model output did not contain structured json_output.")

                return json_output

            elif status == "failed":
                last_error = data.get("error") or "Unknown prediction failure"

        except requests.exceptions.RequestException as e:
            last_error = str(e)

        if attempt < max_retries - 1:
            time.sleep(poll_interval)

    raise RuntimeError(
        f"Replicate structured proofread failed after {max_retries} attempts. "
        f"Last error: {last_error}"
    )

def main():
    """
    Demonstrates proofreading using a sample text with errors.
    """
    sample_text = (
        "Their is many reasons to love programming. It allow you to build cool things, "
        "but sometimes it is hard. When a developer don't write clean code, bugs happens. "
        "Its crucial to write tests, otherwise you will have a bad time. For example, "
        "look at this code: it look simple, but it has some issue."
    )

    print("=" * 60)
    print("GPT-5 Structured Proofreader Demo")
    print("=" * 60)
    print(f"\nOriginal Text:\n{sample_text}\n")
    print("-" * 60)
    print("Calling GPT-5 Structured Proofreading API...")

    try:
        start_time = time.time()
        result = proofread_text(sample_text)
        elapsed_time = time.time() - start_time

        print(f"API call succeeded in {elapsed_time:.2f} seconds.\n")

        print("=" * 60)
        print("PROOFREAD & CORRECTED TEXT:")
        print("=" * 60)
        print(result["corrected_text"])
        print()

        print("=" * 60)
        print("DETAILED CORRECTIONS:")
        print("=" * 60)
        for i, correction in enumerate(result["corrections"], 1):
            print(f"Correction #{i}:")
            print(f"  [Original]  : \"{correction['original_phrase']}\"")
            print(f"  [Corrected] : \"{correction['corrected_phrase']}\"")
            print(f"  [Category]  : {correction['category'].upper()}")
            print(f"  [Reason]    : {correction['explanation']}")
            print()

        print("=" * 60)
        print("OVERALL FEEDBACK:")
        print("=" * 60)
        print(result["overall_feedback"])
        print("=" * 60)

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
