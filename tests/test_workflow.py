import pytest
from workflows import Workflow, Task

def test_workflow_execution():
    # create a simple workflow with two tasks
    task1 = Task(name='task1', action=lambda: 1)
    task2 = Task(name='task2', action=lambda: 2)
    workflow = Workflow(tasks=[task1, task2])

    # execute the workflow
    results = workflow.run()

    # check if the results are as expected
    assert results == [1, 2], f"expected [1, 2], got {results}"

def test_workflow_empty():
    # test a workflow with no tasks
    workflow = Workflow(tasks=[])

    # executing should return an empty list
    results = workflow.run()
    
    assert results == [], f"expected [], got {results}"

def test_single_task_workflow():
    # test a workflow with a single task
    task = Task(name='single_task', action=lambda: 'done')
    workflow = Workflow(tasks=[task])

    results = workflow.run()
    
    assert results == ['done'], f"expected ['done'], got {results}"

# TODO: add more tests for error handling and edge cases