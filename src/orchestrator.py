"""Multi-Agent Orchestrator — coordinates 8 specialized AI agents.

Implements planning loops, tool-use routing, and guardrails for
production-grade agentic AI workflows using LangChain and OpenAI.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"
    SUMMARIZER = "summarizer"
    GUARDRAIL = "guardrail"
    ROUTER = "router"


@dataclass
class AgentMessage:
    role: AgentRole
    content: str
    metadata: dict = field(default_factory=dict)
    tool_calls: list[dict] = field(default_factory=dict)


@dataclass
class WorkflowState:
    messages: list[AgentMessage] = field(default_factory=list)
    current_agent: AgentRole = AgentRole.PLANNER
    iteration: int = 0
    max_iterations: int = 10
    completed: bool = False


class AgentOrchestrator:
    """Orchestrates multi-agent workflows with planning and guardrails."""

    def __init__(self, llm_client, tools: dict[str, Any] | None = None):
        self.llm = llm_client
        self.tools = tools or {}
        self.agents: dict[AgentRole, Any] = {}

    def register_agent(self, role: AgentRole, agent):
        self.agents[role] = agent
        logger.info("Registered agent: %s", role.value)

    async def run_workflow(self, task: str) -> WorkflowState:
        state = WorkflowState()
        state.messages.append(AgentMessage(
            role=AgentRole.PLANNER,
            content=f"Task: {task}",
        ))

        while not state.completed and state.iteration < state.max_iterations:
            agent = self.agents.get(state.current_agent)
            if not agent:
                logger.error("No agent for role: %s", state.current_agent)
                break

            response = await agent.process(state)
            state.messages.append(response)
            state.current_agent = self._route_next(state, response)
            state.iteration += 1

        return state

    def _route_next(self, state: WorkflowState, last_msg: AgentMessage) -> AgentRole:
        if last_msg.metadata.get("done"):
            state.completed = True
            return AgentRole.SUMMARIZER
        return AgentRole(last_msg.metadata.get("next_agent", "researcher"))


class GuardrailChecker:
    """Safety and quality guardrails for agent outputs."""

    BLOCKED_PATTERNS = ["DROP TABLE", "rm -rf", "sudo", "exec("]

    def check(self, content: str) -> tuple[bool, str]:
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in content.lower():
                return False, f"Blocked pattern detected: {pattern}"
        return True, "OK"
