# Replicate Structured API Guide

This guide provides a clean, barebones reference for using the Replicate API for structured, schema-constrained predictions (e.g., using `openai/gpt-5-structured` or similar models). It removes all specific bank/PDF processing logic and provides a reusable, generic implementation.

---

## 1. API Endpoint & Authentication

All requests to the Replicate Structured Model API are authenticated via an API token passed in the `Authorization` header.

* **Endpoint:** `POST https://api.replicate.com/v1/models/openai/gpt-5-structured/predictions`
* **Headers:**
  ```http
  Authorization: Bearer <REPLICATE_API_TOKEN>
  Content-Type: application/json
  Prefer: wait
  ```
  *(Note: The `Prefer: wait` header encourages the API to return the response synchronously if it completes within the gateway timeout limit.)*

---

## 2. Request Payload Structure

The payload defines the underlying model, the desired structured JSON output schema, the input files (encoded as base64 Data URIs), and the text prompt.

```json
{
  "input": {
    "model": "gpt-5",
    "json_schema": {
      "format": {
        "type": "json_schema",
        "name": "<schema_name>",
        "schema": {
          "type": "object",
          "properties": {
            "<field_name>": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "field1": {"type": "string"},
                  "field2": {"type": "number"}
                },
                "required": ["field1", "field2"],
                "additionalProperties": false
              }
            }
          },
          "required": ["<field_name>"],
          "additionalProperties": false
        }
      }
    },
    "input_item_list": [
      {
        "role": "user",
        "content": [
          {
            "type": "input_file",
            "filename": "<filename.ext>",
            "file_data": "data:<mime-type>;base64,<base64_encoded_data>"
          },
          {
            "type": "input_text",
            "text": "<your_prompt_here>"
          }
        ]
      }
    ],
    "enable_web_search": false
  }
}
```

---

## 3. Handling Files (Base64 Data URIs)

When sending files to the Replicate API, you must encode the file to base64 and prepend the corresponding Data URI scheme:

```python
import base64

def encode_file_to_base64(file_path: str, mime_type: str) -> str:
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{encoded_string}"
```

---

## 4. Barebones Reusable Implementation

Below is a clean, dependency-minimal Python function to handle payload construction, calling the API, polling for asynchronous status updates, and extracting the validated JSON result.

```python
import os
import time
import requests
from typing import Dict, Any, Optional

def query_replicate_structured(
    prompt: str,
    schema: Dict[str, Any],
    file_base64: Optional[str] = None,
    filename: Optional[str] = None,
    api_token: Optional[str] = None,
    max_retries: int = 3,
    poll_interval: float = 3.0
) -> Dict[str, Any]:
    """
    Sends a prompt and an optional file to the Replicate Structured API, 
    enforcing a custom JSON schema on the output. Handles polling and retries.
    """
    token = api_token or os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        raise ValueError("Replicate API token must be provided or set in REPLICATE_API_TOKEN environment variable.")

    # 1. Build Payload
    content_list = []
    
    if file_base64 and filename:
        content_list.append({
            "type": "input_file",
            "filename": filename,
            "file_data": file_base64
        })
        
    content_list.append({
        "type": "input_text",
        "text": prompt
    })

    payload = {
        "input": {
            "model": "gpt-5",
            "json_schema": schema,
            "input_item_list": [
                {
                    "role": "user",
                    "content": content_list
                }
            ],
            "enable_web_search": False
        }
    }

    # 2. Call the API
    endpoint = "https://api.replicate.com/v1/models/openai/gpt-5-structured/predictions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            poll_url = data.get("urls", {}).get("get")
            
            # 3. Poll if prediction is asynchronous (starting/processing)
            while status in ["starting", "processing"]:
                time.sleep(poll_interval)
                poll_resp = requests.get(poll_url, headers={"Authorization": f"Bearer {token}"})
                poll_resp.raise_for_status()
                data = poll_resp.json()
                status = data.get("status")
            
            # 4. Handle prediction outcome
            if status == "succeeded":
                output = data.get("output", {})
                json_output = output.get("json_output")
                
                # Fallback to text parsing if json_output is nested as a string
                if not json_output and "text" in output:
                    import json
                    try:
                        json_output = json.loads(output["text"])
                    except json.JSONDecodeError:
                        raise ValueError("Failed to parse the model's text output as JSON.")
                
                return json_output
                
            elif status == "failed":
                last_error = data.get("error") or "Unknown prediction failure"
                
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            
        if attempt < max_retries - 1:
            time.sleep(5.0)  # Wait before retrying on failure
            
    raise RuntimeError(f"Replicate structured query failed after {max_retries} attempts. Last error: {last_error}")
```

---

## 5. Usage Example

Here is how you would call the clean function with custom schemas:

```python
# 1. Define the output format using standard JSON Schema
user_schema = {
    "format": {
        "type": "json_schema",
        "name": "book_info",
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "author": {"type": "string"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["title", "author", "tags"],
            "additionalProperties": False
        }
    }
}

# 2. Run the request
result = query_replicate_structured(
    prompt="Extract the main book details from the provided context.",
    schema=user_schema
)

print(result)
# Output matches the schema:
# {
#     "title": "...",
#     "author": "...",
#     "tags": ["...", "..."]
# }
```
