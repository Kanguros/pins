import pytest

from pins.scenario.base import Scenario


class TestScenarioWithImplementation:
    class MyScenario(Scenario):
        def __init__(self, arg1):
            pass

    class MyScenario2(Scenario):
        def __init__(self, arg1, arg2, defarg=None):
            self.arg1 = arg1
            self.arg2 = arg2

        def execute(self):
            return [self.arg1, self.arg2]

        def analyze(self, results):
            return True

    def test_list_with_subclasses(self):
        available_scenarios = Scenario.get_available()
        assert self.MyScenario in available_scenarios.values()
        assert self.MyScenario2 in available_scenarios.values()

    def test_raise_notimplementederror(self):
        scenario = self.MyScenario("arg")
        with pytest.raises(NotImplementedError):
            scenario.execute()
        with pytest.raises(NotImplementedError):
            scenario.analyze(None)
