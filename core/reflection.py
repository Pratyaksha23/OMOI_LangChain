import re
import json
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field, ValidationError
from core.llm import model

class ReflectionOutput(BaseModel):
    reflection: str = Field(description="One short sentence reflecting on how they seem to feel")
    encouragement: str = Field(description="One short encouraging sentence")
    activity: str = Field(description="One suggestion starting with 'Tomorrow, try starting your day with...'")

template = """
You are a supportive journal companion.

Journal:
{journal}

Emotions noticed today: {emotion}

Respond ONLY with a valid JSON object in this exact format, no extra text:
{{
  "reflection": "one short sentence reflecting on how they seem to feel",
  "encouragement": "one short encouraging sentence",
  "activity": "one suggestion starting with 'Tomorrow, try starting your day with...'"
}}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["journal", "emotion"]
)


def _summarize_emotion(emotion: dict) -> str:
    top = sorted(emotion.items(), key=lambda x: x[1], reverse=True)[:3]
    summary = ", ".join(f"{label} ({pct}%)" for label, pct in top if pct > 0)
    return summary or "no strong emotions detected"


def _extract_json_block(text: str) -> dict | None:
    """
    Finds the LAST {...} block in the text that contains the keys we actually need.
    This skips over stray JSON the model might generate elsewhere (like an
    emotion breakdown) and targets the one that matches our schema.
    """
    # Find all {...} blocks, including across multiple lines
    matches = re.findall(r"\{[^{}]*\}", text, re.DOTALL)

    for match in matches:
        try:
            parsed = json.loads(match)
            if all(key in parsed for key in ("reflection", "encouragement", "activity")):
                return parsed
        except json.JSONDecodeError:
            continue

    return None


def generate_reflection(journal, emotion):
    chain = prompt | model
    emotion_summary = _summarize_emotion(emotion)

    raw_response = chain.invoke({"journal": journal, "emotion": emotion_summary})
    print("---- RAW MODEL OUTPUT ----")
    print(raw_response.content)
    print("--------------------------")

    parsed_dict = _extract_json_block(raw_response.content)

    if parsed_dict:
        try:
            result = ReflectionOutput(**parsed_dict)
            return result.model_dump()
        except ValidationError as e:
            print("---- VALIDATION ERROR ----")
            print(e)
            print("---------------------------")

    print("---- COULD NOT FIND VALID JSON ----")
    return {
        "reflection": "Couldn't generate a reflection this time.",
        "encouragement": "",
        "activity": ""
    }
