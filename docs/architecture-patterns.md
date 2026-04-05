# Multi-Agent Architecture Patterns

## Supervisor Pattern
A central supervisor agent delegates tasks to specialized worker agents
and aggregates results. Best for well-defined workflows where task
decomposition is straightforward.

## Collaborative Pattern
Agents communicate peer-to-peer without a central coordinator.
Each agent has its own memory and can initiate conversations
with other agents. Best for exploratory tasks.

## Pipeline Pattern
Agents are chained sequentially — output of one becomes input to the next.
Similar to Unix pipes. Best for data transformation workflows.

## Voting Pattern
Multiple agents process the same input independently, and a
consensus mechanism selects the best result. Improves reliability
for critical decisions.