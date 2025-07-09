# YAML Configuration System

This document describes the new YAML-based configuration system that follows Click best practices for configuration file handling.

## Overview

The new configuration system provides a clean separation between configuration file defaults and CLI options, using Click's `ctx.default_map` mechanism. This approach is based on the pattern described at: https://jwodder.github.io/kbits/posts/click-config/

## Key Features

1. **YAML Configuration Files**: Use YAML instead of complex Python configuration
2. **Click Integration**: Leverages Click's built-in `ctx.default_map` for defaults
3. **CLI Override**: Command-line options always override config file values
4. **Type Safety**: Automatic type conversion through Click's parameter system
5. **Modular Decorators**: Reusable decorators for common patterns

## Available Decorators

### `yaml_config_option()`

Adds a `--config` option that reads YAML files and sets Click defaults.

```python
@yaml_config_option(default="config.yaml")
@click.option("--name", default="test")
@click.command()
def my_command(name: str):
    pass
```

### `export_show_options()`

Adds standard `--export` and `--show` options for output formatting.

```python
@export_show_options
@click.command()
def my_command(export: tuple[str, ...], show: tuple[str, ...]):
    pass
```

## Configuration File Format

### Basic Structure

```yaml
# Export formats (corresponds to --export option)
export:
    - json
    - csv

# Output formats (corresponds to --show option)
show:
    - table
    - rich

# Panorama connection settings
panorama:
    hostname: "panorama.example.com"
    username: "admin"
    api_version: "v11.1"
    verify_ssl: false

# File-based data sources
files:
    - device_group: "Production"
      security_rules: "data/prod_rules.json"
      address_objects: "data/prod_addresses.json"
      address_groups: "data/prod_groups.json"
```

### Command-Specific Settings

For command groups, you can specify per-command defaults:

```yaml
# Global defaults
export: [json]
show: [table]

# Command-specific overrides
shadowing:
    export: [csv, xml]
    threshold: 10

advanced_analysis:
    show: [rich]
    advanced: true
```

## Migration from Old System

### Old Approach (AppConfig.option)

```python
@AppConfig.option()
@click.option("--device-groups", multiple=True)
def my_command(config: AppConfig, device_groups: tuple[str]):
    # Complex config merging logic
    pass
```

### New Approach

```python
@yaml_config_option()
@export_show_options
@click.option("--device-groups", multiple=True)
def my_command(device_groups: tuple[str], export: tuple[str, ...], show: tuple[str, ...]):
    # Click handles config merging automatically via ctx.default_map
    pass
```

## Benefits

1. **Simpler Code**: No complex configuration merging logic needed
2. **Better Testing**: Easy to test individual components
3. **Click Native**: Uses Click's built-in configuration mechanisms
4. **Type Safety**: Automatic type conversion and validation
5. **Flexible**: Easy to add new options and configuration patterns

## Usage Examples

### Basic Command

```python
@yaml_config_option()
@export_show_options
@click.option("--threshold", type=int, default=10)
@click.command()
def analyze(threshold: int, export: tuple[str, ...], show: tuple[str, ...]):
    \"\"\"Analyze with YAML configuration support.\"\"\"
    click.echo(f"Threshold: {threshold}")
    click.echo(f"Export: {export}")
    click.echo(f"Show: {show}")
```

### Command with Panorama Options

```python
@yaml_config_option()
@export_show_options
@click.option("--panorama-hostname", help="Panorama hostname")
@click.option("--panorama-username", help="Panorama username")
@click.command()
def panorama_command(panorama_hostname: str, panorama_username: str, export: tuple[str, ...], show: tuple[str, ...]):
    \"\"\"Command with Panorama integration.\"\"\"
    # Configuration from YAML will be available as defaults
    pass
```

### Running Commands

```bash
# Use config file defaults
policy-inspector analyze --config myconfig.yaml

# Override specific options
policy-inspector analyze --config myconfig.yaml --threshold 20 --export xml

# Use multiple export formats
policy-inspector analyze --export json --export csv --show table --show rich
```

## Error Handling

- **Missing config file**: Silently ignored, uses built-in defaults
- **Invalid YAML**: Clear error message with details
- **Invalid option values**: Click's normal validation applies
- **Type conversion**: Automatic via Click's type system

## Best Practices

1. **Use specific decorators**: Prefer `export_show_options` over manual option definitions
2. **Config file optional**: Don't require config files, provide sensible defaults
3. **CLI override**: Always allow CLI options to override config file values
4. **Document options**: Use clear help text for all options
5. **Validate early**: Let Click handle type validation automatically
