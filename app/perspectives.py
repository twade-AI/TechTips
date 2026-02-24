"""
Perspectives Engine — The Dialogical Partner

Generates three distinct perspectives on education innovation questions:
  1. The Guardian (cautious/evidence-first)
  2. The Radical (transformative/reimagine)
  3. The Pragmatist (balanced/what-works)

Each perspective includes supporting and contradicting evidence,
followed by a verdict on which has the strongest support.
"""

import json
import os
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

SYSTEM_PROMPT = """You are an expert panel on education innovation for 11-18 year olds.
You specialise in pedagogy, digital technology in education, and enterprise/employability skills.

When given a question, you MUST respond with a JSON object (no markdown, no backticks) containing exactly these fields:

{
  "question": "the original question",
  "cautious": {
    "name": "The Guardian",
    "stance": "A 2-3 sentence summary of this cautious perspective",
    "argument": "A detailed 150-200 word argument from someone who values proven methods, evidence-based practice, and warns against untested innovation. They respect tradition but aren't anti-change — they want rigorous evidence before disrupting what works.",
    "supporting_evidence": ["3-4 specific pieces of evidence, research, or real-world examples that support this view"],
    "contradicting_evidence": ["2-3 specific pieces of evidence that challenge or weaken this view"]
  },
  "radical": {
    "name": "The Radical",
    "stance": "A 2-3 sentence summary of this radical redesign perspective",
    "argument": "A detailed 150-200 word argument from someone who believes the current education system is fundamentally broken for the modern world. They advocate for bold reimagining — project-based learning, abolishing exams, AI-first classrooms, student-led curricula, etc.",
    "supporting_evidence": ["3-4 specific pieces of evidence, research, or real-world examples that support this view"],
    "contradicting_evidence": ["2-3 specific pieces of evidence that challenge or weaken this view"]
  },
  "pragmatic": {
    "name": "The Pragmatist",
    "stance": "A 2-3 sentence summary of this balanced, implementation-focused perspective",
    "argument": "A detailed 150-200 word argument from someone who bridges both camps. They believe in meaningful innovation but within realistic constraints — budgets, teacher workload, Ofsted, parental expectations. They focus on what can actually be implemented at scale.",
    "supporting_evidence": ["3-4 specific pieces of evidence, research, or real-world examples that support this view"],
    "contradicting_evidence": ["2-3 specific pieces of evidence that challenge or weaken this view"]
  },
  "debate": "A 100-150 word section where the three perspectives directly engage with each other's arguments — agreements, disagreements, and challenges.",
  "verdict": {
    "strongest": "cautious|radical|pragmatic",
    "explanation": "A 100-150 word analysis of which perspective currently has the strongest evidentiary support and why. Be honest and specific — don't just pick the middle ground by default."
  }
}

Ground your arguments in real research, frameworks, and examples where possible (EEF, Hattie, PISA, Ofsted research reviews, specific school/MAT examples, international comparisons).
Focus on the UK education context (11-18, Key Stage 3/4/5) but draw on international evidence."""


async def generate_perspectives(question: str) -> dict:
    """Generate three perspectives on an education innovation question."""
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": question}
        ],
    )
    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    return json.loads(raw)


async def generate_followup(question: str, original: dict, followup: str) -> str:
    """Generate a follow-up response continuing the debate."""
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system="You are the same expert panel from a previous education debate. Continue the discussion based on the follow-up question. Respond in clear prose, referencing the three perspectives (The Guardian, The Radical, The Pragmatist) and how they would each respond to this follow-up.",
        messages=[
            {"role": "user", "content": f"Original question: {question}\n\nPrevious debate summary:\n{json.dumps(original, indent=2)}\n\nFollow-up question: {followup}"},
        ],
    )
    return message.content[0].text
