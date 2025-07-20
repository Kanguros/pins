from policy_inspector.scenario import Scenario


class ExampleScenario(Scenario):
    """Mock example scenario for testing."""

    name = "example"

    def __init__(self, panorama, **kwargs):
        super().__init__(panorama, **kwargs)

    def run(self):
        """Run the example scenario."""
        return {"result": "success"}
