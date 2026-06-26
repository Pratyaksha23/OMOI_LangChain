from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel, Field
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

parser = PydanticOutputParser(pydantic_object=EmotionBreakdown)

template = """
Analyze the emotional content of this journal entry.

Journal:
{journal}

Estimate a percentage (whole number, 0-100) for each emotion below.
The percentages MUST add up to EXACTLY 100. Adjust your estimates as needed so the total is exactly 100, not 99 or 101.

{format_instructions}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["journal"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)


def _normalize_to_100(emotion: dict) -> dict:
    """
    Rescales percentages so they sum to exactly 100, preserving relative proportions.
    Handles the all-zero edge case safely.
    """
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
  #since this is still being tested
    raw_response = chain.invoke({"journal": text})
    print("---- RAW EMOTION MODEL OUTPUT ----")
    print(raw_response.content)
    print("-----------------------------------")

    try:
        result = parser.parse(raw_response.content)
        emotion_dict = result.model_dump()
        return _normalize_to_100(emotion_dict)
    except OutputParserException as e:
        print("---- EMOTION PARSER ERROR ----")
        print(e)
        print("-------------------------------")
        return {field: 0 for field in EmotionBreakdown.model_fields}
