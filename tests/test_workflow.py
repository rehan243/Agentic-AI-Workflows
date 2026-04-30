import pytest
from workflows import Workflow, ExecutionError

# test case for successful workflow execution
def test_workflow_execution():
    workflow = Workflow()
    result = workflow.run("example_task")
    assert result == "expected_output"

# test case for handling an error in the workflow
def test_workflow_execution_error():
    workflow = Workflow()
    with pytest.raises(ExecutionError):
        workflow.run("failing_task")

# test case for checking task registration
def test_task_registration():
    workflow = Workflow()
    workflow.register_task("new_task", lambda: "new_output")
    assert "new_task" in workflow.tasks

# test case for verifying task execution order
def test_task_execution_order():
    workflow = Workflow()
    workflow.register_task("first_task", lambda: "first")
    workflow.register_task("second_task", lambda: "second")
    
    execution_order = workflow.run_all(["first_task", "second_task"])
    assert execution_order == ["first", "second"]

# TODO: add more tests for edge cases and complex workflows