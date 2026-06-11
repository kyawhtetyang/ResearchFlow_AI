from app.agents.planner import plan_research
from app.agents.report_agent import generate_report
from app.agents.search_agent import search_sources
from app.agents.summarizer_agent import summarize_findings


def test_research_agents_generate_a_recruiter_ready_report():
    query = "What AI Engineer project should follow a production RAG assistant?"

    plan = plan_research(query)
    sources = search_sources(query)
    findings = summarize_findings(query, sources)
    report = generate_report(query, plan, findings, sources)

    assert len(plan) >= 5
    assert len(sources) >= 5
    assert len(findings) >= 4
    assert "ResearchFlow AI" in report
    assert "Recruiter-Facing Proof" in report
    assert "OpenAI Agents SDK" in report
