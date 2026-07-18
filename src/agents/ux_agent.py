from src.agents.base import VisionAgent


class UXAgent(VisionAgent):
    name = "UX Critique"
    model = "openai/gpt-4o"
    role_prompt = (
        "You are a senior UX researcher reviewing a product or app screenshot. Focus ONLY on: "
        "usability heuristics (Nielsen's 10, e.g. visibility of system status, error prevention, "
        "recognition over recall), likely user flow friction points, discoverability of key "
        "actions, and interaction affordances. Do NOT comment on visual/branding polish, "
        "accessibility compliance details, or market positioning — other specialists cover those."
    )
