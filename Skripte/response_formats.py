import json

with open('Daten/Basisdaten/parteien.json', 'r', encoding='utf-8') as f:
    allowed_parties = json.load(f)

# STEP #1: Persona
persona_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "persona",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Ein realistischer deutscher Name"},
                "alter": {"type": "integer", "description": "Alter zwischen 16 und 100"},
                "beruf": {"type": "string", "description": "Aktueller oder letzter Beruf"},
                "wohnort": {"type": "string", "description": "Stadt oder Region in Deutschland"},
                "beschreibung": {"type": "string", "description": "Detaillierte Personenbeschreibung"},
                "politische_einstellung": {"type": "string", "description": "Politische Grundhaltung"},
                "kernthemen": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 10,
                    "description": "Liste der wichtigsten politischen Themen"
                },
                "wahlverhalten": {"type": "string", "description": "Typisches Wahlverhalten"},
                "sorgen": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 10,
                    "description": "Liste aktueller Sorgen"
                },
                "hoffnungen": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 10,
                    "description": "Liste von Hoffnungen/Wünschen"
                }
            }
        }
    }
}

# STEP #2: Wahlomat
wahlomat_response_format = {
    "type": "json_schema",
     "json_schema": {
        "name": "wahlomat_response",
        "schema": {
            "type": "object",
            "properties": {
                "antworten": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "these_id": {"type": "integer", "minimum": 1, "maximum": 35},
                            "position": {"type": "integer", "enum": [-1, 0, 1]},
                            "begruendung": {"type": "string", "minLength": 20, "maxLength": 500}
                        }
                    },
                    "minItems": 35,
                    "maxItems": 35
                }
            }
        }
    }
}

# STEP #3: Judge
judge_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "judge_response",
        "schema": {
            "type": "object",
            "properties": {
                "matches": {
                    "type": "object",
                    "properties": {
                        "CDU": {"type": "number", "minimum": 0, "maximum": 100},
                        "SPD": {"type": "number", "minimum": 0, "maximum": 100},
                        "GRÜNE": {"type": "number", "minimum": 0, "maximum": 100},
                        "FDP": {"type": "number", "minimum": 0, "maximum": 100},
                        "LINKE": {"type": "number", "minimum": 0, "maximum": 100},
                        "AFD": {"type": "number", "minimum": 0, "maximum": 100}
                    },
                    "required": allowed_parties
                },
                "analyse": {
                    "type": "string",
                    "minLength": 100,
                    "maxLength": 2000
                }
            }
        }
    }
}

# STEP #4: Finale Wahl
final_choice_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "final_choice_response",
        "schema": {
            "type": "object",
            "properties": {
                "partei_wahl": {
                    "type": "string",
                    "enum": allowed_parties,
                    "description": "Eine der Parteien"
                },
                "begruendung": {
                    "type": "string",
                    "minLength": 50,
                    "maxLength": 1000,
                    "description": "Deine Begründung zur Wahl der Partei"
                },
                "sicherheit": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Prozentwert"
                }
            }
        }
    }
}