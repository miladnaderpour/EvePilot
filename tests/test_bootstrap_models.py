from evepilot.bootstrap.preparation.models import FlowAction, FlowDefinition
from evepilot.bootstrap.preparation.models import FlowStartup, FlowStateMarker, FlowStep


def test_flow_model_defaults() -> None:
    flow = FlowDefinition(
        name="example",
        version=1,
        states={
            "user_exec_prompt": FlowStateMarker(
                name="user_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+>\s*$"],
            )
        },
        steps=[
            FlowStep(
                name="enter-enable-mode",
                action=FlowAction.SEND,
                when_state="user_exec_prompt",
                send="enable\n",
            )
        ],
    )

    assert flow.startup == FlowStartup()
    assert flow.startup.wake_enter == "\r\n"
    assert flow.steps[0].next is None
    assert flow.steps[0].optional is False
