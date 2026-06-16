import pytest
from workflows import Workflow, Step

# this test checks if a workflow can be created successfully
def test_workflow_creation():
    workflow = Workflow(name="test_workflow")
    assert workflow.name == "test_workflow"
    assert workflow.steps == []

# this test checks if steps can be added to the workflow
def test_add_step():
    workflow = Workflow(name="test_workflow")
    step = Step(name="step_1", action="do_something")
    workflow.add_step(step)
    
    assert len(workflow.steps) == 1
    assert workflow.steps[0].name == "step_1"

# this test checks if the workflow can execute its steps
def test_execute_steps():
    workflow = Workflow(name="test_workflow")
    step_1 = Step(name="step_1", action="do_something")
    step_2 = Step(name="step_2", action="do_something_else")
    
    workflow.add_step(step_1)
    workflow.add_step(step_2)
    
    results = workflow.execute()
    
    assert results == ["step_1 executed", "step_2 executed"]  # assuming this is expected output

# TODO: add more tests for error handling and edge cases