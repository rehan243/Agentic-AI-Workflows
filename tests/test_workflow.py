import pytest
from workflows import Workflow

# testing the basic functionality of the Workflow class
def test_workflow_initialization():
    # ensure a workflow initializes with the correct attributes
    workflow = Workflow(name="test_workflow", steps=["step1", "step2"])
    assert workflow.name == "test_workflow"
    assert workflow.steps == ["step1", "step2"]

def test_workflow_execute():
    # testing the execution of the workflow
    workflow = Workflow(name="test_workflow", steps=["step1", "step2"])
    
    # assuming there's a method to execute the workflow
    result = workflow.execute()
    
    # check if the execution returns expected output
    assert result == "execution successful"

def test_workflow_add_step():
    # testing adding a step to the workflow
    workflow = Workflow(name="test_workflow", steps=["step1"])
    workflow.add_step("step2")
    
    assert "step2" in workflow.steps
    assert len(workflow.steps) == 2

def test_workflow_remove_step():
    # testing removing a step from the workflow
    workflow = Workflow(name="test_workflow", steps=["step1", "step2"])
    workflow.remove_step("step1")
    
    assert "step1" not in workflow.steps
    assert len(workflow.steps) == 1

# TODO: add more tests for edge cases and error handling