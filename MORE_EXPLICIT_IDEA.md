Read, analyze and develop.

# Explicit is better than implicit

I've changed how the `Scenario` are defined. Instead of playing with magic by creating a `click` command in customized group, I've decided to explicitly create a click command for each scenario. Even if that means repating the same options and some code.

## Scenario structure

### The simpliest possible version

```
├─custom_scenario
│   ├─ __init__.py  # Because its a package
│   ├─ cmd.py  # Module with click command, under the same name as package

```

### More granular

```
├─custom_scenario
│   ├─ __init__.py  # Because its a package
│   ├─ cmd.py  # Module with click command, under the same name as package
│   ├─ scenario.py  # Module with Scenario implementation; imported in command.py
│   ├─ exporter.py  # Exporter class with custom export methods; imported in scenario.py
│   ├─ displayer.py  # Exporter class with custom export methods; imported in scenario.py

```
## Issues

### Scenario and command

```
@click.command(name=Shadowing.name.lower())
@display_option
@export_options
@click.pass_context
def shadowing(ctx: click.Context, **kwargs):
    """Dynamic scenario command."""
    run_scenario(Shadowing, **kwargs)

```

It's an example of my idea of scenario command. I don't know how to pass exporter and displayer formats of a Shadowing scenario to those options. I could pass Scenario to them and get that info from scenario but it will require another things to remember for someone to implement new scenario command. 


### ScenarioLoader class

It's too damn complex. It has to look for builtin scenario commands (in cmd.py) and for provided path to packages with scenario command like that: `my_scenarios.custom_scenario`.

It also should implement running an `example` command. 
```
pins run example
```

### Command `list` is not working

Class `LazyGroup` is missing a method for listing scenarios/commands and getting some data to show. 

## Q&A

### Why Exporter and Displayer classes gets Scenario instance when executed?

Because exporting or display format might need other information than the scenerio analysis results. 

### Why Scenario class define PanoramaConnector?

To have the possibility to override it and provide different class. Meant for extending Panorama with new methods to get new data. 