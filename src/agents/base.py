from src.openrouter_client import build_json_schema, call_openrouter, parse_json_response
from src.schemas import AgentFindings, AgentResult

_JSON_INSTRUCTIONS = (
    'Respond with strict JSON only, matching this shape: '
    '{"score": <0-100 integer>, "summary": "<1-2 sentence overview>", '
    '"findings": [{"category": "<short label>", '
    '"severity": "low|medium|high|critical", "description": "<what you observed>", '
    '"recommendation": "<concrete, actionable fix>"}]}. '
    "List 3-6 concrete findings, most important first. No prose outside the JSON."
)


class VisionAgent:
    name: str
    model: str
    role_prompt: str

    async def run(self, image_data_url: str) -> AgentResult:
        try:
            response_format = build_json_schema(AgentFindings, "agent_findings")
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{self.role_prompt}\n\n{_JSON_INSTRUCTIONS}"},
                        {"type": "image_url", "image_url": {"url": image_data_url}},
                    ],
                }
            ]
            raw = await call_openrouter(self.model, messages, response_format=response_format)
            parsed = parse_json_response(raw)
            validated = AgentFindings.model_validate(parsed)
            return AgentResult(
                agent_name=self.name,
                model_used=self.model,
                score=validated.score,
                summary=validated.summary,
                findings=validated.findings,
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                model_used=self.model,
                score=0,
                summary="This agent failed to produce a result.",
                findings=[],
                error=str(e),
            )
