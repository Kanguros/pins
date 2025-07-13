# CLI Reference

Policy Inspector provides the `pins` command-line interface for analyzing firewall policies.

## Quick Start

```bash
# List available scenarios
pins list

# Run an example with sample data
pins run example shadowing-basic

# Run actual analysis on your Panorama
pins run shadowing --panorama-hostname your-panorama.company.com \
     --panorama-username admin --device-groups "Production"

# Get help for any command
pins --help
pins run --help
```

## Main Commands

The `pins` CLI has two main commands:

- `pins list` - List available scenarios
- `pins run` - Execute analysis scenarios

```{eval-rst}
.. click:: policy_inspector.cli:main
   :prog: pins
   :nested: full
```

## Command Groups

### List Available Scenarios

```{eval-rst}
.. click:: policy_inspector.cli:main_list
   :prog: pins list
```

### Run Scenarios

The `run` command group provides subcommands for executing different analysis scenarios:

```{eval-rst}
.. click:: policy_inspector.cli:main_run
   :prog: pins run
   :nested: full
```

#### Basic Shadowing Analysis

Run basic shadowing analysis:

```{eval-rst}
.. click:: policy_inspector.cli:run_shadowing
   :prog: pins run shadowing
```

#### Advanced Shadowing Analysis

Run advanced shadowing analysis with additional value checking:

```{eval-rst}
.. click:: policy_inspector.cli:run_shadowingvalue
   :prog: pins run shadowingvalue
```

#### Example Execution

Run predefined examples with mock data:

```{eval-rst}
.. click:: policy_inspector.cli:run_example
   :prog: pins run example
```

## Configuration Options

The CLI supports various configuration methods:

### Environment Variables

- `PINS_PANORAMA_HOSTNAME`: Panorama server hostname
- `PINS_PANORAMA_USERNAME`: Username for authentication
- `PINS_PANORAMA_PASSWORD`: Password for authentication
- `PINS_PANORAMA_API_VERSION`: API version (default: v11.1)

### Configuration File

Use `--config` option to specify a YAML configuration file:

```yaml
panorama:
    hostname: panorama.example.com
    username: admin
    password: secret
    api_version: v11.1
    verify_ssl: false

export:
    output_dir: ./reports
    formats:
        - json
        - html

show:
    formats:
        - table
        - text
```

### Command Line Options

All configuration can be overridden via command-line options. Use `--help` with any command to see available options.

## Examples

### Basic Usage

```bash
# List all available scenarios
pins list

# Run shadowing analysis with live Panorama
pins run shadowing --panorama-hostname panorama.example.com \
     --panorama-username admin --device-groups "Production"

# Run example with table output
pins run example shadowing-basic --show table

# Export results to JSON
pins run example shadowingvalue-basic --export json --export-dir ./reports
```

### Advanced Usage

```bash
# Run analysis on multiple device groups
pins run shadowing --panorama-hostname panorama.example.com \
     --panorama-username admin \
     --device-groups "DG1" "DG2" --show table

# Use configuration file
pins run shadowing --config config.yaml --show json --export html

# Run with specific API version
pins run shadowingvalue --panorama-hostname panorama.local \
     --panorama-api-version v10.2 --device-groups "Production"
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Connection error

## Troubleshooting

### Common Issues

**Authentication Failures:**

```bash
# Verify credentials
pins run shadowing --panorama-hostname your-panorama \
     --panorama-username admin --device-groups "Production" --show text
```

**SSL Certificate Issues:**

```bash
# Disable SSL verification
pins run shadowing --panorama-hostname panorama.local \
     --panorama-no-verify-ssl --device-groups "Production"
```

**Configuration Problems:**

```bash
# Validate configuration file
pins run example shadowing-basic --config your-config.yaml
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
pins --verbose run shadowing --panorama-hostname panorama.example.com \
     --device-groups "Production"
```

## See Also

- {doc}`../guides/configuration` - Detailed configuration guide
- {doc}`../guides/usage` - Usage examples and patterns
- {doc}`../examples/basic-usage` - Basic usage examples
- {doc}`../api/index` - API reference documentation
