import json
from pathlib import Path
from typing import Dict, Optional

from llm_client import OpenAIClient
from schemas import PersonaSchema
from response_formats import persona_response_format
from prompt_templates import PERSONA_GENERATION_TEMPLATE

def step1_create_persona(
    gles_data: Dict,
    client: OpenAIClient
) -> Optional[PersonaSchema]:
    
    # Load news for context
    news_path = Path("Daten/Basisdaten/news.txt")
    news_data = news_path.read_text(encoding="utf-8")
    
    # Format the prompt
    user_prompt = PERSONA_GENERATION_TEMPLATE.format(
        gles_data=json.dumps(gles_data, ensure_ascii=False),
        news_data=news_data
    )
    
    # Create system prompt for generation of persona
    system_prompt = (
        "Du bist ein erfahrener Experte für Wählerprofile und Demografie. "
        "Erstelle eine realistische, detaillierte Persona basierend auf den Daten."
    )

    result, error = client.structured_call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_format=persona_response_format,
        response_model=PersonaSchema
    )

    return result
