from src.openrouter_client import build_json_schema, call_openrouter, parse_json_response
from src.schemas import AgentResult, FinalReport

_ROLE_PROMPT = (
    "You are the lead design director synthesizing four specialist critiques (Visual Analysis, "
    "UX Critique, Accessibility, Market Research) of the same product/app screenshot into one "
    "final report for the product team. You will be given each specialist's JSON output "
    "(score, summary, findings). Merge and prioritize their findings — do not simply concatenate "
    "them; identify the handful of issues that matter most across all four lenses, resolve any "
    "overlap, and write a concise executive summary."
)

_JSON_INSTRUCTIONS = (
    'Respond with strict JSON only, matching this shape: '
    '{"overall_score": <0-100 integer, a holistic average weighted by severity>, '
    '"executive_summary": "<2-4 sentence overview for a product team>", '
    '"prioritized_recommendations": [{"category": "<short label>", '
    '"severity": "low|medium|high|critical", "description": "<what and why>", '
    '"recommendation": "<concrete, actionable fix>"}]}. '
    "List the 5-8 most important recommendations across all specialists, most critical first. "
    "No prose outside the JSON."
)


class ReportAgent:
    name = "Final Report"
    model = "openai/gpt-4.1"

    async def run(self, agent_results: dict[str, AgentResult]) -> FinalReport:
        context_blocks = []
        for key, res in agent_results.items():
            context_blocks.append(
                f"### {res.agent_name} (model: {res.model_used}, error: {res.error or 'none'})\n"
                f"{res.model_dump_json(include={'score', 'summary', 'findings'})}"
            )
        context = "\n\n".join(context_blocks)

        response_format = build_json_schema(FinalReport, "final_report")
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": f"{_ROLE_PROMPT}\n\n{context}\n\n{_JSON_INSTRUCTIONS}"}],
            }
        ]
        raw = await call_openrouter(self.model, messages, response_format=response_format, max_tokens=2000)
        parsed = parse_json_response(raw)
        return FinalReport.model_validate(parsed)
