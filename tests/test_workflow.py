import pytest
from workflows import Workflow, Task  # assuming these are the main modules

def test_workflow_initialization():
    # test if workflow initializes correctly
    workflow = Workflow(name="test_workflow")
    assert workflow.name == "test_workflow"
    assert workflow.tasks == []

def test_adding_task():
    # test if a task can be added to the workflow
    workflow = Workflow(name="test_workflow")
    task = Task(name="test_task", action=lambda: "done")
    workflow.add_task(task)
    
    assert len(workflow.tasks) == 1
    assert workflow.tasks[0].name == "test_task"

def test_workflow_execution():
    # test if workflow executes tasks correctly
    workflow = Workflow(name="test_workflow")
    task1 = Task(name="task1", action=lambda: "result1")
    task2 = Task(name="task2", action=lambda: "result2")
    
    workflow.add_task(task1)
    workflow.add_task(task2)
    
    results = workflow.execute()  # assuming this runs all tasks in order
    assert results == ["result1", "result2"]

def test_empty_workflow_execution():
    # test if executing an empty workflow returns an empty result
    workflow = Workflow(name="empty_workflow")
    results = workflow.execute()
    assert results == []  # should return empty list if no tasks