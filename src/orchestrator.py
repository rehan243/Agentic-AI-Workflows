"""multi-agent orchestrator — coordinates 8 specialized ai agents.

implements planning loops, tool-use routing, and guardrails for
production-grade agentic ai workflows using langchain and openai.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Tuple, Dict, List

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
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class WorkflowState:
    messages: List[AgentMessage] = field(default_factory=list)
    current_agent: AgentRole = AgentRole.PLANNER
    iteration: int = 0
    max_iterations: int = 10
    completed: bool = False


class AgentOrchestrator:
    """orchestrates multi-agent workflows with planning and guardrails."""

    def __init__(self, llm_client, tools: Optional[Dict[str, Any]] = None):
        self.llm = llm_client
        self.tools = tools or {}
        self.agents: Dict[AgentRole, Any] = {}

    def register_agent(self, role: AgentRole, agent):
        self.agents[role] = agent
        logger.info("registered agent: %s", role.value)

    async def run_workflow(self, task: str) -> WorkflowState:
        state = WorkflowState()
        state.messages.append(AgentMessage(
            role=AgentRole.PLANNER,
            content=f"Task: {task}",
        ))

        while not state.completed and state.iteration < state.max_iterations:
            agent = self.agents.get(state.current_agent)
            if not agent:
                logger.error("no agent for role: %s", state.current_agent)
                break

            try:
                response = await agent.process(state)
                state.messages.append(response)
                state.current_agent = self._route_next(state, response)
                state.iteration += 1
            except Exception as e:
                logger.error(f"error processing with agent {state.current_agent}: {e}")
                break

        return state

    def _route_next(self, state: WorkflowState, last_msg: AgentMessage) -> AgentRole:
        if last_msg.metadata.get("done"):
            state.completed = True
            return AgentRole.SUMMARIZER
        return AgentRole(last_msg.metadata.get("next_agent", "researcher"))


class GuardrailChecker:
    """safety and quality guardrails for agent outputs."""

    BLOCKED_PATTERNS = ["DROP TABLE", "rm -rf", "sudo", "exec("]

    def check(self, content: str) -> Tuple[bool, str]:
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in content.lower():
                return False, f"blocked pattern detected: {pattern}"
        return True, "OK"