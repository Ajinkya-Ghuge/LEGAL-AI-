"""
LangGraph Workflow Orchestrator
Flow: Upload → Intake Agent → Compliance Agent → Risk Agent → Audit Agent → Finish
"""
from datetime import datetime
from typing import TypedDict, Any

try:
    from langgraph.graph import StateGraph, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False

from . import intake_agent, compliance_agent, risk_agent, audit_agent


class WorkflowState(TypedDict):
    document_text: str
    doc_name: str
    intake_result: dict
    compliance_result: dict
    risk_result: dict
    audit_result: dict
    agent_log: list


def _build_langgraph():
    """Build LangGraph state machine."""
    graph = StateGraph(WorkflowState)

    graph.add_node("intake",     intake_agent.run)
    graph.add_node("compliance", compliance_agent.run)
    graph.add_node("risk",       risk_agent.run)
    graph.add_node("audit",      audit_agent.run)

    graph.set_entry_point("intake")
    graph.add_edge("intake",     "compliance")
    graph.add_edge("compliance", "risk")
    graph.add_edge("risk",       "audit")
    graph.add_edge("audit",      END)

    return graph.compile()


def run_compliance_workflow(document_text: str, doc_name: str = "document.pdf") -> dict:
    """
    Main entry point — runs all 4 agents in sequence.
    Returns flat result dict for the UI.
    """
    print(f"\n{'='*50}")
    print(f"  MedComply AI — Starting Workflow")
    print(f"  Document: {doc_name}")
    print(f"{'='*50}")

    initial_state: WorkflowState = {
        "document_text":    document_text,
        "doc_name":         doc_name,
        "intake_result":    {},
        "compliance_result": {},
        "risk_result":      {},
        "audit_result":     {},
        "agent_log":        [],
    }

    if HAS_LANGGRAPH:
        print("  Using LangGraph orchestration")
        try:
            workflow = _build_langgraph()
            final_state = workflow.invoke(initial_state)
        except Exception as e:
            print(f"  LangGraph error: {e} — falling back to sequential")
            final_state = _run_sequential(initial_state)
    else:
        print("  LangGraph not available — using sequential pipeline")
        final_state = _run_sequential(initial_state)

    return _flatten_result(final_state)


def _run_sequential(state: dict) -> dict:
    """Fallback: run agents sequentially without LangGraph."""
    state = intake_agent.run(state)
    state = compliance_agent.run(state)
    state = risk_agent.run(state)
    state = audit_agent.run(state)
    return state


def _flatten_result(state: dict) -> dict:
    """Merge all agent outputs into one flat dict for the UI."""
    intake     = state.get("intake_result", {})
    compliance = state.get("compliance_result", {})
    risk       = state.get("risk_result", {})
    audit      = state.get("audit_result", {})

    return {
        # Top-level KPIs
        "compliance_score": compliance.get("compliance_score", 0),
        "compliance_status": compliance.get("overall_status", "UNKNOWN"),
        "risk_level":       risk.get("risk_level", "UNKNOWN"),
        "risk_score":       risk.get("risk_score", 0),
        "audit_verdict":    audit.get("audit_verdict", "UNKNOWN"),
        "timestamp":        audit.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "doc_name":         state.get("doc_name", ""),

        # Agent outputs
        "intake":     intake,
        "compliance": compliance,
        "risk":       risk,
        "audit":      audit,

        # Convenience fields for templates
        "violations":      compliance.get("violations", []),
        "recommendations": compliance.get("recommendations", []),
        "risk_factors":    risk.get("risk_factors", []),
        "chronology":      audit.get("medical_chronology", []),
        "executive_summary": audit.get("executive_summary", ""),
        "agent_log":       state.get("agent_log", []),

        # Patient info
        "patient_name":  intake.get("patient_name", "Unknown"),
        "hospital_name": intake.get("hospital_name", "Unknown"),
        "doctor_name":   intake.get("doctor_name", "Unknown"),
        "diagnosis":     intake.get("diagnosis", []),
    }
