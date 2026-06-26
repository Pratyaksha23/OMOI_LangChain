from langchain_core.prompts import PromptTemplate
from core.llm import model
from utils.storage import get_last_n_days

MIN_ENTRIES_FOR_SUMMARY = 3

template = """
You are summarizing a user's journal entries from the past week.

Entries:
{entries}

Summarize:
1. Dominant emotions this week
2. Any trend (improving / worsening / steady)
3. Topics that came up more than once
4. One encouraging observation

Weekly Summary:
"""

prompt = PromptTemplate(input_variables=["entries"], template=template)

def _format_emotion(emotion: dict) -> str:
    # show only the top 2 emotions per entry, keeps the prompt concise
    top = sorted(emotion.items(), key=lambda x: x[1], reverse=True)[:2]
    return ", ".join(f"{label} {pct}%" for label, pct in top)

def generate_weekly_summary():
    entries = get_last_n_days(7)

    if len(entries) < MIN_ENTRIES_FOR_SUMMARY:
        return f"Not enough entries yet for a weekly summary — you have {len(entries)} this week. Come back after journaling a bit more."

    entries_str = "\n\n".join(
        f"[{e['date']}] {e['journal']} (top emotions: {_format_emotion(e['emotion'])})"
        for e in entries
    )

    chain = prompt | model
    result = chain.invoke({"entries": entries_str})
    return result.content