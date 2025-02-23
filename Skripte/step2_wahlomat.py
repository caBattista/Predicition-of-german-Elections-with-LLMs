import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from llm_client import OpenAIClient
from schemas import PersonaSchema, WahlomatSchema
from response_formats import wahlomat_response_format
from prompt_templates import WAHLOMAT_TEMPLATE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_party_programs() -> str:
    program_dir = Path("Daten/Basisdaten/wahlprogramme")
    programs = []

    for party_file in [
        "CDU.txt",
        "SPD.txt",
        "GRÜNE.txt",
        "FDP.txt",
        "LINKE.txt",
        "AFD.txt",
    ]:
        try:
            content = (program_dir / party_file).read_text(encoding="utf-8")
            programs.append(content)
        except Exception as e:
            logger.warning(f"Could not load {party_file}: {e}")

    return "\n\n".join(programs)


def load_news() -> str:
    news_path = Path("Daten/Basisdaten/news.txt")
    try:
        return news_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not load news: {e}")
        return ""


def load_wahlomat_questions() -> List[Dict]:
    questions_path = Path("Daten/Basisdaten/wahlomat_fragen.json")
    try:
        return json.loads(questions_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Could not load wahlomat questions: {e}")
        return []


def step2_wahlomat(
    persona: PersonaSchema, client: OpenAIClient
):
    # Load required data
    questions = load_wahlomat_questions()
    if not questions:
        logger.error("No wahlomat questions available")
        return None

    news_data = load_news()
    party_programs = load_party_programs()

    # Format the prompt
    user_prompt = WAHLOMAT_TEMPLATE.format(
        #persona_str=json.dumps(persona.model_dump(), ensure_ascii=False),
        persona_str=json.dumps(persona, ensure_ascii=False),
        news_data=news_data,
        party_programs=party_programs,
        questions=json.dumps(questions, ensure_ascii=False),
    )

    # Make the API call
    system_prompt = (
        "Du bist jetzt die beschriebene Persona."
        "Beantworte die Wahl-O-Mat-Fragen aus ihrer Perspektive."
    )

    result, error = client.structured_call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_format=wahlomat_response_format,
        response_model=WahlomatSchema,
    )
    
    return result