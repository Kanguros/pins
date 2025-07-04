
I would like to allow users to define their own scenarios #file:scenario.py  including being able to execute them from CLI. In the same way as Shadowing and Advanced Shadowing are invoked #file:cli.py 
pins run shadowing ...
Figure out how to do it. Do not modify code just yet, provide me your idea. Make sure it is simple and straightforward. 
#codebase #search 

Analyze it once again but this time take into considiration that other arguments than `panorama` could be required. As Shadowing scenario require a `device_groups`. They might require different arguments. Also, how to define those scenarios so that click would nicely print help doc and required and optional params.



```
import click
from policy_inspector.scenario import Scenario

class MyCustomScenario(Scenario):
    """
    My custom scenario with a threshold.
    """
    cli_options = [
        click.Option(["--threshold"], type=int, required=True, help="Threshold value for the check."),
        click.Option(["--mode"], type=click.Choice(["fast", "slow"]), default="fast", help="Mode of operation."),
    ]

    def __init__(self, panorama, threshold, mode, **kwargs):
        super().__init__(panorama, **kwargs)
        self.threshold = threshold
        self.mode = mode
    # ... rest of scenario ...
```


```
def add_scenario_commands(main_run_group):
    for name, scenario_cls in Scenario.get_available().items():
        params = getattr(scenario_cls, "cli_options", [])

        @click.command(name, help=scenario_cls.__doc__)
        @panorama_options
        @exclude_check_option()
        @show_option()
        @export_formats()
        def scenario_command(**kwargs):
            # ... instantiate and run scenario ...
            pass

        for param in params:
            scenario_command = param(scenario_command)

        main_run_group.add_command(scenario_command)
```