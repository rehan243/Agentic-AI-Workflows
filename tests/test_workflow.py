import pytest
from workflows import Workflow, Task

# creating a simple workflow with tasks
@pytest.fixture
def sample_workflow():
    task1 = Task(name="task1", action=lambda: "result1")
    task2 = Task(name="task2", action=lambda: "result2")
    workflow = Workflow(tasks=[task1, task2])
    return workflow

def test_workflow_execution(sample_workflow):
    # testing if the tasks execute as expected
    results = sample_workflow.run()
    assert results[0] == "result1"
    assert results[1] == "result2"

def test_workflow_task_count(sample_workflow):
    # checking if the workflow has the right amount of tasks
    assert len(sample_workflow.tasks) == 2

def test_workflow_task_names(sample_workflow):
    # ensuring task names are set correctly
    task_names = [task.name for task in sample_workflow.tasks]
    assert "task1" in task_names
    assert "task2" in task_names

# TODO: add more tests for error handling and edge cases