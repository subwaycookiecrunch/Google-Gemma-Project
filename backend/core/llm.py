"""
PARASITE EVOLVED — Shared LLM Module
Centralized Gemma 4 integration for all AI-powered components.
Uses Gemma 4 (26B instruction-tuned) via Google GenAI API.
"""

import os
import json
import re
from typing import Optional
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()
console = Console()

# Gemma 4 model — the open-weight model powering PARASITE EVOLVED
GEMMA_MODEL = "gemma-4-27b-it"
# Fallback options in priority order
GEMMA_FALLBACK_MODELS = ["gemma-4-12b-it", "gemma-3-27b-it", "gemini-2.0-flash"]


def _get_working_model_name(genai_module) -> Optional[str]:
    """Try Gemma 4 models in order, return first available."""
    for model_name in [GEMMA_MODEL] + GEMMA_FALLBACK_MODELS:
        try:
            model = genai_module.GenerativeModel(model_name)
            # Quick test to verify model exists
            return model_name
        except Exception:
            continue
    return None


def get_gemma_model():
    """Get a configured Gemma 4 model instance."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model_name = _get_working_model_name(genai)
        if not model_name:
            console.print("[dim red]  ⚠ No Gemma/Gemini model available[/]")
            return None
        
        console.print(f"[dim green]  🧠 Using model: {model_name}[/]")
        return genai.GenerativeModel(model_name)
    except ImportError:
        console.print("[dim red]  ⚠ google-generativeai not installed. pip install google-generativeai[/]")
        return None
    except Exception as e:
        console.print(f"[dim red]  ⚠ Gemma initialization error: {e}[/]")
        return None


# Keep backward compatibility
get_gemini_model = get_gemma_model


def call_gemma(prompt: str, system_instruction: str = "", max_tokens: int = 2048) -> Optional[str]:
    """Call Gemma 4 with a prompt and return the response text."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model_name = _get_working_model_name(genai)
        if not model_name:
            return None
        
        model = genai.GenerativeModel(
            model_name,
            system_instruction=system_instruction if system_instruction else None
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        console.print(f"[dim red]  ⚠ Gemma API error: {e}[/]")
        return None


# Keep backward compatibility
call_gemini = call_gemma


def call_gemma_json(prompt: str, system_instruction: str = "", max_tokens: int = 2048) -> Optional[dict]:
    """Call Gemma 4 and parse the response as JSON."""
    raw = call_gemma(prompt, system_instruction, max_tokens)
    if not raw:
        return None
    
    try:
        # Try direct parse first
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown fences
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object in the text
        brace_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON array
        bracket_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if bracket_match:
            try:
                return json.loads(bracket_match.group(0))
            except json.JSONDecodeError:
                pass
    
    console.print(f"[dim red]  ⚠ Failed to parse Gemma JSON response[/]")
    return None


# Keep backward compatibility
call_gemini_json = call_gemma_json
