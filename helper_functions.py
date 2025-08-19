from typing import Optional, List, Dict, Any, Tuple, Union, Literal, TypedDict 
import json

def retrieve_prompt(prompt_path: str, mode: str = "r", encoding: str = 'utf-8') -> str: 
    with open(prompt_path, mode, encoding=encoding) as file: 
        prompt_text = file.read()
    return prompt_text

def retrieve_template(template_path: str, mode: str = "r", encoding: str = 'utf-8') -> str: 
    with open(template_path, mode, encoding=encoding) as file: 
        template_text = file.read()
    return template_text

def retrieve_style(style_path: str, mode: str = "r", encoding: str = 'utf-8') -> str: 
    with open(style_path, mode, encoding=encoding) as file: 
        style_text = file.read()
    return style_text



def retrieve_transcript(transcript_path: str, mode: str = "r", encoding: str = 'utf-8') -> str: 
    with open(transcript_path, mode, encoding=encoding) as file: 
        transcript_text = file.read()
    return transcript_text

def parse_json_content(content: str) -> Union[Dict, List, Any, None]:
    """
    Parse JSON content that may be wrapped in markdown code blocks.
    
    Args:
        content (str): The content string that may contain JSON data
                      wrapped in markdown code blocks or plain JSON
    
    Returns:
        Union[Dict, List, Any, None]: Parsed JSON object or None if no valid JSON found
    """
    if not content or not content.strip():
        return None
    
    # Remove all newlines (both escaped and actual) and clean up the content
    if '\\n' in content:
        content = content.replace('\\n', '').strip()
    if '\n' in content:
        content = content.replace('\n', '').strip()
    
    try:
        # Check if content is wrapped in markdown code blocks
        if content.startswith('```json') and content.endswith('```'):
            # Extract JSON from markdown code block
            json_content = content[7:-3].strip()  # Remove ```json and ```
            return json.loads(json_content)
        elif content.startswith('```') and content.endswith('```'):
            # Handle generic code blocks that might contain JSON
            json_content = content[3:-3].strip()  # Remove ``` and ```
            return json.loads(json_content)
        elif content.startswith('```json\n') and content.endswith('\n```'):
            # Handle code blocks with newlines
            json_content = content[7:-4].strip()  # Remove ```json\n and \n```
            return json.loads(json_content)
        else:
            # Try to parse as plain JSON
            return json.loads(content)
    except json.JSONDecodeError:
        # If JSON parsing fails, return None instead of raising error
        return content