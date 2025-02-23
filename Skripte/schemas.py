from pydantic import BaseModel, Field, field_validator
from typing import List
from enum import Enum

class Party(str, Enum):
    CDU = "CDU"
    SPD = "SPD"
    GRÜNE = "GRÜNE"
    FDP = "FDP"
    LINKE = "LINKE"
    AFD = "AFD"

# STEP #1: Persona
class PersonaSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    alter: int = Field(..., description="Alter der Person")
    beruf: str = Field(..., min_length=2, max_length=100)
    wohnort: str = Field(..., min_length=2, max_length=100)
    beschreibung: str = Field(..., min_length=50, max_length=1000)
    politische_einstellung: str = Field(..., min_length=20, max_length=500)
    kernthemen: List[str] = Field(..., min_length=2, max_length=10)
    wahlverhalten: str = Field(..., min_length=20, max_length=500)
    sorgen: List[str] = Field(..., min_length=1, max_length=10)
    hoffnungen: List[str] = Field(..., min_length=1, max_length=10)

    @field_validator("alter")
    def validate_alter(cls, v):
        if not (16 <= v <= 100):
            raise ValueError("Alter muss zwischen 16 und 100 Jahren liegen")
        return v

    @field_validator("kernthemen", "sorgen", "hoffnungen")
    def validate_list_length(cls, v):
        if not (1 <= len(v) <= 10):
            raise ValueError("Liste muss zwischen 1 und 10 Einträge haben")
        return v

# STEP #2: Wahlomat
class WahlomatAnswer(BaseModel):
    these_id: int = Field(..., ge=1, le=35)
    position: int = Field(..., description="Position zu der These (-1, 0, 1)")
    begruendung: str = Field(..., min_length=20, max_length=500)

    @field_validator("position")
    def validate_position(cls, v):
        if v not in [-1, 0, 1]:
            raise ValueError("Position muss -1 (dagegen), 0 (neutral) oder 1 (dafür) sein")
        return v

class WahlomatSchema(BaseModel):
    antworten: List[WahlomatAnswer] = Field(..., min_length=35, max_length=35)

    @field_validator("antworten")
    def validate_unique_theses(cls, v):
        these_ids = [a.these_id for a in v]
        if len(these_ids) != len(set(these_ids)):
            raise ValueError("Jede These darf nur einmal beantwortet werden")
        if sorted(these_ids) != list(range(1, 36)):
            raise ValueError("Es müssen alle Thesen von 1 bis 35 beantwortet werden")
        return v

# STEP #3: Judge
class JudgePartyMatch(BaseModel):
    CDU: float = Field(..., ge=0, le=100)
    SPD: float = Field(..., ge=0, le=100)
    GRÜNE: float = Field(..., ge=0, le=100)
    FDP: float = Field(..., ge=0, le=100)
    LINKE: float = Field(..., ge=0, le=100)
    AFD: float = Field(..., ge=0, le=100)

    @field_validator("*")
    def validate_percentage(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Prozentwert muss zwischen 0 und 100 liegen")
        return round(v, 2)  # Round to 2 decimal places

class JudgeSchema(BaseModel):
    matches: JudgePartyMatch
    analyse: str = Field(..., min_length=100, max_length=2000)

    @field_validator("analyse")
    def validate_analyse_length(cls, v):
        words = v.split()
        if not (20 <= len(words) <= 400):
            raise ValueError("Analyse muss zwischen 20 und 400 Wörter haben")
        return v

# STEP #4: Finale Wahl
class FinalChoiceSchema(BaseModel):
    partei_wahl: Party
    begruendung: str = Field(..., min_length=50, max_length=1000)
    sicherheit: int = Field(..., ge=0, le=100)

    @field_validator("begruendung")
    def validate_begruendung_length(cls, v):
        words = v.split()
        if not (10 <= len(words) <= 200):
            raise ValueError("Begründung muss zwischen 10 und 200 Wörter haben")
        return v

    @field_validator("sicherheit")
    def validate_sicherheit(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Sicherheit muss zwischen 0 und 100 Prozent liegen")
        return v 