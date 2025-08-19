import openai
import json 
import os
from groq import Groq 
from typing import Optional, List, Dict, Any, Tuple, Union, Literal, TypedDict 
from pydantic import BaseModel, Field, ConfigDict
from helper_functions import parse_json_content
from openai import OpenAI
from typing import Optional, Callable
from openai import OpenAI, APIError
from xai_sdk import Client
from xai_sdk.chat import user, system
import time 

def deep_research_grok(prompt: str, model: str = 'grok-4', api_key: str = os.getenv("XAI_API_KEY")) -> str: 
    client = Client(api_key=api_key)
    response = client.chat.completions.create(
    model = model, 
    messages = [{'role': 'user', 'content': prompt}], 
    search_parameters = {
        'mode': 'on', 
        'sources': [
            {'type': 'web'}, 
        ], 
        'return_citations': True, 
        'max_search_results': 10, 
        'from_date': '2025-01-01'
    }, 
    stream = True)
    return response.choices[0].message.content

def stream_llama(prompt: str, api_key: str, model: str = 'meta-llama/llama-4-scout-17b-16e-instruct') -> str: 
    client = Groq(api_key=api_key)
    start_time = time.time(); print('API HIT')
    if model == 'meta-llama/llama-4-scout-17b-16e-instruct': 
        max_completion_tokens = 8192
    else: 
        max_completion_tokens = 12000
    completion = client.chat.completions.create(
    model=model,
    messages=[
      {
        "role": "user",
        "content": prompt
      }
    ],
    temperature=0,
    max_completion_tokens=max_completion_tokens,
    top_p=0.95,
    stream=True,
    stop=None)

    full_response = ""
    for chunk in completion:
        content = chunk.choices[0].delta.content
        if content is not None: 
            full_response += content
    end_time = time.time(); print(f'Time Taken: {end_time - start_time}')
    return full_response

def stream_openai(model: str, prompt: str,
                        api_key: str = None,
                        temperature: float = 0,
                        max_tokens: int = 10000) -> str:
    client = OpenAI(api_key=api_key)
    full_text = ""

    with client.responses.stream(
        model=model,
        input=prompt,
        temperature=temperature,
        max_output_tokens=max_tokens
    ) as stream:
        print("Streaming output:\n")
        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
                full_text += event.delta
            elif event.type == "response.completed":
                print("\n\n✅ Finished streaming")
        
        final_response = stream.get_final_response()
        # Sync collected text with final output (in case of deltas missed):
        if not full_text.strip():
            full_text = final_response.output_text
    
    return full_text

def call_gpt5(
    prompt: str,
    api_key: str,
    model: str = "gpt-5",
    on_delta: Optional[Callable[[str], None]] = None,) -> str:
    """
    Streams GPT-5 output and returns the final text.
    If `on_delta` is provided, it's called with each text chunk as it arrives.
    """
    client = OpenAI(api_key=api_key)

    # Stream the response; placing stable instructions FIRST encourages prompt-cache hits.
    print('API hit'); start_time = time.time()
    stream = client.responses.create(
        model=model,
        input=prompt,
        text={"verbosity": "high"},
        reasoning={"effort": "high"},
        stream=True,
    )

    final_chunks = []
    try:
        for event in stream:
            etype = getattr(event, "type", None)

            # Token/text deltas arrive here
            if etype == "response.output_text.delta":
                chunk = event.delta
                if on_delta:
                    on_delta(chunk)
                else:
                    print(chunk, end="", flush=True)
                final_chunks.append(chunk)

            # Stream finishes here
            elif etype == "response.completed":
                break

            # Surface any server errors
            elif etype == "error":
                # `event` includes an error payload with details
                raise RuntimeError(getattr(event, "error", event))
    except APIError as e:
        raise RuntimeError(f"OpenAI API error: {e}") from e
    end_time = time.time(); print(f'Time Taken: {end_time - start_time}')
    return "".join(final_chunks)

def call_grok(prompt: str, api_key: str, model: str = "grok-3") -> str:
    """
    Sends a synchronous API request to the Grok model and returns full output.
    """

    # Create client
    client = Client(api_key=api_key, timeout=360)

    # Create chat session and send the message
    chat = client.chat.create(model=model, temperature=0)
    chat.append(system(prompt))

    # Call synchronously (no streaming)
    response = chat.sample()

    # Assuming single message output from the model
    return response.content

def stream_grok(prompt, api_key, model: str = 'grok-4-0709'):
    print(f'API hit'); start_time = time.time()
    client = Client(api_key=api_key, timeout = 360)
    chat = client.chat.create(model=model,temperature=0)
    chat.append(user(prompt))
    full_response = ""
    for response, chunk in chat.stream(): 
        print(chunk.content, end="", flush=True)
        full_response += chunk.content
    end_time = time.time(); print(f'Time Taken: {end_time - start_time}')
    return full_response