import pytest
from agentic_workflows import Workflow, Task

# test the basic workflow execution
def test_workflow_execution():
    task1 = Task(name="task1", action=lambda: "result1")
    task2 = Task(name="task2", action=lambda: "result2")
    workflow = Workflow(tasks=[task1, task2])

    results = workflow.run()  # assuming run executes tasks in order
    assert results == ["result1", "result2"]  # check if results match expected

# test task failure handling
def test_task_failure():
    task1 = Task(name="task1", action=lambda: "result1")
    task2 = Task(name="task2", action=lambda: 1 / 0)  # this will raise an error
    workflow = Workflow(tasks=[task1, task2])

    with pytest.raises(ZeroDivisionError):  # expect an error here
        workflow.run()

# test if workflow can handle empty tasks
def test_empty_workflow():
    workflow = Workflow(tasks=[])
    results = workflow.run()
    assert results == []  # should return empty results for empty workflow

# test workflow with mixed results
def test_mixed_results():
    task1 = Task(name="task1", action=lambda: "result1")
    task2 = Task(name="task2", action=lambda: None)  # this one returns None
    workflow = Workflow(tasks=[task1, task2])

    results = workflow.run()
    assert results == ["result1", None]  # check mixed results