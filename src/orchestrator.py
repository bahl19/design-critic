import asyncio

from fastapi import HTTPException

from src.agents.accessibility_agent import AccessibilityAgent
from src.agents.market_agent import MarketAgent
from src.agents.report_agent import ReportAgent
from src.agents.ux_agent import UXAgent
from src.agents.visual_agent import VisualAgent
from src.openrouter_client import to_data_url
from src.schemas import AgentResult, AnalyzeResponse, FinalReport, Finding, Severity


def _fallback_report(agent_results: dict[str, AgentResult], reason: str) -> FinalReport:
    """Used only if the report agent itself fails — degrade to a mechanical
    rollup of the specialist findings rather than losing the response."""
    succeeded = [r for r in agent_results.values() if r.error is None]
    overall_score = round(sum(r.score for r in succeeded) / len(succeeded)) if succeeded else 0
    top_findings: list[Finding] = []
    for r in succeeded:
        top_findings.extend(r.findings)
    order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3}
    top_findings.sort(key=lambda f: order[f.severity])
    return FinalReport(
        overall_score=overall_score,
        executive_summary=(
            "Automated synthesis unavailable (report agent error: "
            f"{reason}). Showing the highest-severity findings across specialists instead."
        ),
        prioritized_recommendations=top_findings[:8],
    )


async def run_analysis(image_bytes: bytes, content_type: str) -> AnalyzeResponse:
    data_url = to_data_url(image_bytes, content_type)

    agents = {
        "visual": VisualAgent(),
        "ux": UXAgent(),
        "accessibility": AccessibilityAgent(),
        "market": MarketAgent(),
    }
    tasks = [agent.run(data_url) for agent in agents.values()]
    settled = await asyncio.gather(*tasks, return_exceptions=True)

    agent_results: dict[str, AgentResult] = {}
    errors: list[str] = []
    for key, agent, outcome in zip(agents.keys(), agents.values(), settled):
        if isinstance(outcome, Exception):
            agent_results[key] = AgentResult(
                agent_name=agent.name,
                model_used=agent.model,
                score=0,
                summary="This agent failed to produce a result.",
                error=str(outcome),
            )
            errors.append(f"{agent.name}: {outcome}")
        else:
            agent_results[key] = outcome
            if outcome.error:
                errors.append(f"{agent.name}: {outcome.error}")

    if all(r.error for r in agent_results.values()):
        raise HTTPException(
            502, "All analysis agents failed; check OPENROUTER_API_KEY and OpenRouter status."
        )

    try:
        final_report = await ReportAgent().run(agent_results)
    except Exception as e:
        final_report = _fallback_report(agent_results, str(e))
        errors.append(f"Final Report: {e}")

    return AnalyzeResponse(
        final_report=final_report,
        agents=agent_results,
        partial_failure=bool(errors),
        errors=errors,
    )
