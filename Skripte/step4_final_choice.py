import json
import logging
from pathlib import Path
from typing import Optional

from llm_client import OpenAIClient
from schemas import PersonaSchema, WahlomatSchema, JudgeSchema, FinalChoiceSchema
from response_formats import final_choice_response_format
from prompt_templates import FINAL_CHOICE_TEMPLATE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def step4_final_choice(
    persona: PersonaSchema,
    wahlomat_answers: WahlomatSchema,
    judge_result: JudgeSchema,
    client: OpenAIClient
) -> Optional[FinalChoiceSchema]:
 
    # Load required data
    news_path = Path("Daten/Basisdaten/news.txt")
    news_data = news_path.read_text(encoding="utf-8")

    # Load party programs
    program_dir = Path("Daten/Basisdaten/wahlprogramme")
    party_programs = []
    for party_file in ["CDU.txt", "SPD.txt", "GRÜNE.txt", "FDP.txt", "LINKE.txt", "AFD.txt"]:
        content = (program_dir / party_file).read_text(encoding="utf-8")
        party_programs.append(content)
    
    # Format the prompt
    # user_prompt = FINAL_CHOICE_TEMPLATE.format(
    #     persona_str=json.dumps(persona.model_dump(), ensure_ascii=False),
    #     answers_str=json.dumps(wahlomat_answers.model_dump(), ensure_ascii=False),
    #     judge_str=json.dumps(judge_result.model_dump(), ensure_ascii=False),
    #     news_data=news_data,
    #     party_programs=party_programs
    # )

    user_prompt = FINAL_CHOICE_TEMPLATE.format(
        persona_str=json.dumps(persona, ensure_ascii=False),
        answers_str=json.dumps(wahlomat_answers, ensure_ascii=False),
        judge_str=json.dumps(judge_result, ensure_ascii=False),
        news_data=news_data,
        party_programs=party_programs
    )
    
    # Make the API call
    system_prompt = (
        "Du bist wieder die ursprüngliche Persona. "
        "Treffe deine finale Wahlentscheidung basierend auf allen verfügbaren Informationen."
    )
    
    result, error = client.structured_call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=FinalChoiceSchema,
        response_format=final_choice_response_format
    )
        
    return result