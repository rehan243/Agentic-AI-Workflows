import pytest
from workflows import Workflow, Task

# testing basic workflow behavior
def test_workflow_initialization():
    # create a simple workflow with a couple of tasks
    task1 = Task(name='task1', action=lambda: 'result1')
    task2 = Task(name='task2', action=lambda: 'result2')
    workflow = Workflow(tasks=[task1, task2])
    
    # check if the workflow has the right number of tasks
    assert len(workflow.tasks) == 2
    assert workflow.tasks[0].name == 'task1'
    assert workflow.tasks[1].name == 'task2'

def test_workflow_execution():
    task1 = Task(name='task1', action=lambda: 'result1')
    task2 = Task(name='task2', action=lambda: 'result2')
    workflow = Workflow(tasks=[task1, task2])
    
    results = workflow.execute()
    
    # check if the results are as expected
    assert results == ['result1', 'result2']

def test_workflow_empty():
    workflow = Workflow(tasks=[])
    
    # check if executing an empty workflow returns an empty result
    results = workflow.execute()
    assert results == []

# TODO: add more tests for error handling and edge cases