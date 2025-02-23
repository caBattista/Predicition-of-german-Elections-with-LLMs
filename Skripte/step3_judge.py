import json
import logging
from pathlib import Path
from typing import Optional

from llm_client import OpenAIClient
from schemas import PersonaSchema, WahlomatSchema, JudgeSchema
from response_formats import judge_response_format
from prompt_templates import JUDGE_TEMPLATE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_party_programs() -> str:
    program_dir = Path("Daten/Basisdaten/wahlprogramme")
    programs = []
    
    for party_file in ["CDU.txt", "SPD.txt", "GRÜNE.txt", "FDP.txt", "LINKE.txt", "AFD.txt"]:
        try:
            content = (program_dir / party_file).read_text(encoding="utf-8")
            programs.append(content)
        except Exception as e:
            logger.warning(f"Could not load {party_file}: {e}")
    
    return "\n\n".join(programs)

def step3_judge(
    persona: PersonaSchema,
    wahlomat_answers: WahlomatSchema,
    client: OpenAIClient
) -> Optional[JudgeSchema]:
    
    # Load party programs for context
    party_programs = load_party_programs()
    
    # Format the prompt
    # user_prompt = JUDGE_TEMPLATE.format(
    #     persona_str=json.dumps(persona.model_dump(), ensure_ascii=False),
    #     answers_str=json.dumps(wahlomat_answers.model_dump(), ensure_ascii=False),
    #     party_programs=party_programs
    # )

    user_prompt = JUDGE_TEMPLATE.format(
        persona_str=json.dumps(persona, ensure_ascii=False),
        answers_str=json.dumps(wahlomat_answers, ensure_ascii=False),
        party_programs=party_programs
    )
    
    # Make the API call
    system_prompt = (
        "Du bist ein neutraler Wahlexperte und Politikwissenschaftler."
        "Analysiere die Übereinstimmungen zwischen den Antworten und den Parteipositionen."
    )
    
    result, error = client.structured_call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=JudgeSchema,
        response_format=judge_response_format
    )
    
    return result