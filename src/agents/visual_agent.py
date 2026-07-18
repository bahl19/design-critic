from src.agents.base import VisionAgent


class VisualAgent(VisionAgent):
    name = "Visual Analysis"
    model = "openai/gpt-4o"
    role_prompt = (
        "You are a senior visual/brand design critic reviewing a product or app screenshot. "
        "Focus ONLY on: layout composition, color palette and contrast choices, typography "
        "(font pairing, hierarchy, sizing), visual hierarchy, spacing/alignment, and branding "
        "consistency. Do NOT comment on usability flows, accessibility compliance, or market "
        "positioning — other specialists cover those."
    )
