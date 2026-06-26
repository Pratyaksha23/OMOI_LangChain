# import json
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser
# from langchain.output_parsers import OutputFixingParser
# from pydantic import BaseModel, Field
# from core.llm import model

# class ReflectionOutput(BaseModel):
#     reflection: str = Field(description="One short sentence reflecting on how they seem to feel")
#     encouragement: str = Field(description="One short encouraging sentence")
#     activity: str = Field(description="One suggestion starting with 'Tomorrow, try starting your day with...'")

# parser = PydanticOutputParser(pydantic_object=ReflectionOutput)
# fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)

# template = """
# You are a supportive journal companion.

# Journal:
# {journal}

# Emotions noticed today: {emotion}

# {format_instructions}
# """

# prompt = PromptTemplate(
#     template=template,
#     input_variables=["journal", "emotion"],
#     partial_variables={"format_instructions": parser.get_format_instructions()}
# )


# def _summarize_emotion(emotion: dict) -> str:
#     """Converts the emotion % dict into a plain-text summary instead of JSON,
#     so the model doesn't copy the JSON shape into the wrong part of its output."""
#     top = sorted(emotion.items(), key=lambda x: x[1], reverse=True)[:3]
#     summary = ", ".join(f"{label} ({pct}%)" for label, pct in top if pct > 0)
#     return summary or "no strong emotions detected"


# def generate_reflection(journal, emotion):
#     chain = prompt | model
#     emotion_summary = _summarize_emotion(emotion)

#     raw_response = chain.invoke({"journal": journal, "emotion": emotion_summary})
#     print("---- RAW MODEL OUTPUT ----")
#     print(raw_response.content)
#     print("--------------------------")

#     try:
#         result = fixing_parser.parse(raw_response.content)
#         return result.model_dump()
#     except Exception as e:
#         print("---- PARSER ERROR (even after fix attempt) ----")
#         print(e)
#         print("-------------------------------------------------")
#         return {
#             "reflection": "Couldn't generate a reflection this time.",
#             "encouragement": "",
#             "activity": ""
#         }

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from core.llm import model


class ReflectionOutput(BaseModel):
    reflection: str = Field(
        description="One short sentence reflecting on how they seem to feel."
    )
    encouragement: str = Field(
        description="One short encouraging sentence."
    )
    activity: str = Field(
        description="One suggestion starting with 'Tomorrow, try starting your day with...'"
    )


template = """
You are a supportive journal companion.

Read the journal and the detected emotions.

Return:
- One short reflection.
- One short encouragement.
- One activity suggestion beginning with
  'Tomorrow, try starting your day with...'

Journal:
{journal}

Emotions noticed today:
{emotion}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["journal", "emotion"],
)


def _summarize_emotion(emotion: dict) -> str:
    top = sorted(emotion.items(), key=lambda x: x[1], reverse=True)[:3]
    summary = ", ".join(
        f"{label} ({pct}%)"
        for label, pct in top
        if pct > 0
    )
    return summary or "no strong emotions detected"


def generate_reflection(journal, emotion):
    emotion_summary = _summarize_emotion(emotion)

    # Ask the model to return a ReflectionOutput object directly
    structured_model = model.with_structured_output(ReflectionOutput)

    chain = prompt | structured_model

    try:
        result = chain.invoke(
            {
                "journal": journal,
                "emotion": emotion_summary,
            }
        )

        return result.model_dump()

    except Exception as e:
        print("Reflection generation failed:")
        print(e)

        return {
            "reflection": "Couldn't generate a reflection this time.",
            "encouragement": "",
            "activity": "",
        }