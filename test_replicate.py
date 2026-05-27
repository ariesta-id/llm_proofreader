# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def test_api():
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        print("Error: REPLICATE_API_TOKEN not found in environment.")
        return

    # A very simple schema to test connection and structure
    schema = {
        "format": {
            "type": "json_schema",
            "name": "joke_response",
            "schema": {
                "type": "object",
                "properties": {
                    "setup": {"type": "string"},
                    "punchline": {"type": "string"}
                },
                "required": ["setup", "punchline"],
                "additionalProperties": False
            }
        }
    }

    payload = {
        "input": {
            "model": "gpt-5",
            "json_schema": schema,
            "input_item_list": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Tell me a joke about computer science."
                        }
                    ]
                }
            ],
            "enable_web_search": False
        }
    }

    endpoint = "https://api.replicate.com/v1/models/openai/gpt-5-structured/predictions"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }

    print("Sending request to Replicate Structured API...")
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        status = data.get("status")
        poll_url = data.get("urls", {}).get("get")
        
        print(f"Initial status: {status}")
        while status in ["starting", "processing"]:
            print("Processing... waiting 3 seconds...")
            time.sleep(3)
            poll_resp = requests.get(poll_url, headers={"Authorization": f"Bearer {api_token}"})
            poll_resp.raise_for_status()
            data = poll_resp.json()
            status = data.get("status")
            print(f"Status updated: {status}")

        if status == "succeeded":
            output = data.get("output", {})
            print("\nSuccess! Raw Output:")
            print(output)
        else:
            print(f"\nFailed: Status is {status}")
            print(data.get("error"))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_api()
