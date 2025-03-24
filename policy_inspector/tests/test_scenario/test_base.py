import pytest

from policy_inspector.scenario import Scenario


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

    def test_get_args_empty(self):
        assert Scenario.get_args() == []

    @pytest.mark.parametrize(
        "scenario_class,args",
        [
            (MyScenario, ["arg1"]),
            (MyScenario2, ["arg1", "arg2", "defarg"]),
        ],
    )
    def test_get_args(self, scenario_class, args):
        assert scenario_class.get_args() == args

    def test_list_with_subclasses(self):
        assert Scenario.list() == {self.MyScenario, self.MyScenario2}

    def test_raise_notimplementederror(self):
        scenario = self.MyScenario("arg")
        with pytest.raises(NotImplementedError):
            scenario.execute()

        with pytest.raises(NotImplementedError):
            scenario.analyze(None)
