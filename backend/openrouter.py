"""OpenRouter API client for making LLM requests."""

import httpx
from typing import List, Dict, Any, Optional
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via OpenRouter API.

    Args:
        model: OpenRouter model identifier (e.g., "openai/gpt-4o")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']
            content = message.get('content')
            
            # Handle empty content (known issue with gemini-3-pro-preview)
            if not content or (isinstance(content, str) and len(content.strip()) == 0):
                import sys
                finish_reason = data['choices'][0].get('finish_reason', 'unknown')
                error_msg = f"Model {model} returned empty content (finish_reason: {finish_reason}). This is a known issue with some Gemini models."
                sys.stderr.write(f"{error_msg}\n")
                print(f"Warning: {error_msg}")
                # Return None to indicate failure
                return None

            return {
                'content': content,
                'reasoning_details': message.get('reasoning_details')
            }

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}: {e.response.text[:500]}"
        print(f"Error querying model {model}: {error_msg}")
        import sys
        sys.stderr.write(f"OpenRouter API error for {model}: {error_msg}\n")
        return None
    except httpx.RequestError as e:
        error_msg = f"Request failed: {str(e)}"
        print(f"Error querying model {model}: {error_msg}")
        import sys
        sys.stderr.write(f"OpenRouter request error for {model}: {error_msg}\n")
        return None
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Error querying model {model}: {error_msg}")
        import sys
        sys.stderr.write(f"OpenRouter unexpected error for {model}: {error_msg}\n")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of OpenRouter model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
