import re
import json
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field, ValidationError
from core.llm import model

class EmotionBreakdown(BaseModel):
    happiness: int = Field(description="Percentage 0-100")
    sadness: int = Field(description="Percentage 0-100")
    anger: int = Field(description="Percentage 0-100")
    overstimulated: int = Field(description="Percentage 0-100")
    anxiety: int = Field(description="Percentage 0-100")
    confidence: int = Field(description="Percentage 0-100")
    gratitude: int = Field(description="Percentage 0-100")
    stress: int = Field(description="Percentage 0-100")

template = """
Analyze the emotional content of this journal entry.

Journal:
{journal}

Estimate a percentage (0-100) for each emotion below, based on how strongly it is present.
Do not explain your reasoning. Respond ONLY with a valid JSON object in this exact format, nothing else:

{{"happiness": 0, "sadness": 0, "anger": 0, "overstimulated": 0, "anxiety": 0, "confidence": 0, "gratitude": 0, "stress": 0}}
"""

prompt = PromptTemplate(template=template, input_variables=["journal"])


def _extract_json_block(text: str) -> dict | None:
    matches = re.findall(r"\{[^{}]*\}", text, re.DOTALL)
    for match in matches:
        try:
            parsed = json.loads(match)
            if all(key in parsed for key in EmotionBreakdown.model_fields):
                return parsed
        except json.JSONDecodeError:
            continue
    return None


def _normalize_to_100(emotion: dict) -> dict:
    total = sum(emotion.values())
    if total == 0:
        return emotion
    scaled = {label: round(pct / total * 100) for label, pct in emotion.items()}
    diff = 100 - sum(scaled.values())
    if diff != 0:
        largest_label = max(scaled, key=scaled.get)
        scaled[largest_label] += diff
    return scaled


def analyze_emotion(text):
    chain = prompt | model
    raw_response = chain.invoke({"journal": text})
    print("---- RAW EMOTION MODEL OUTPUT ----")
    print(raw_response.content)
    print("-----------------------------------")

    parsed_dict = _extract_json_block(raw_response.content)

    if parsed_dict:
        try:
            result = EmotionBreakdown(**parsed_dict)
            return _normalize_to_100(result.model_dump())
        except ValidationError as e:
            print("---- EMOTION VALIDATION ERROR ----")
            print(e)
            print("-----------------------------------")

    print("---- COULD NOT FIND VALID EMOTION JSON ----")
    return {field: 0 for field in EmotionBreakdown.model_fields}
