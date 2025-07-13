# Usage Guide

This guide covers advanced usage patterns and features of Policy Inspector.

## Command Structure

Policy Inspector uses a hierarchical command structure with three main commands:

```
pins <command> [command-options]
```

The available commands are:

- `pins list` - List available scenarios
- `pins run` - Execute a scenario (shadowing, shadowingvalue, example)

### Global Options

All commands support standard options like `--help` for detailed usage information.

## Available Commands

### List Command

Display available scenarios:

```bash
pins list
```

This shows all available analysis scenarios with their descriptions and available checks.

### Run Command

Execute analysis scenarios. The `run` command has three subcommands:

#### run shadowing

Analyze security policy for shadowed rules using basic algorithm:

```bash
# Basic shadowing analysis
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production"

# With configuration file
pins run shadowing --config config.yaml

# Multiple device groups
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" "DMZ" "Internal"

# With different output formats
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" \
     --show table

# Export results
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" \
     --export html --export-dir ./reports
```

**Connection Options:**

- `--panorama-hostname HOST` - Panorama hostname or IP
- `--panorama-username USER` - Username for authentication
- `--panorama-password PASS` - Password (use environment variables recommended)
- `--panorama-api-version VERSION` - API version (default: v11.1)
- `--panorama-verify-ssl` - Enable SSL certificate verification

**Analysis Options:**

- `--device-groups DG` - Device group(s) to analyze (can be specified multiple times)
- `--config FILE` - Configuration file path

**Output Options:**

- `--show FORMAT` - Display format (text, table, json) - can specify multiple
- `--export FORMAT` - Export format (html, json, csv) - can specify multiple
- `--export-dir DIR` - Directory for exported files (default: current directory)

#### run shadowingvalue

Run advanced shadowing analysis with more sophisticated algorithms:

```bash
# Advanced shadowing analysis
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production"

# With table output
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" \
     --show table

# Export to multiple formats
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" \
     --export json html --export-dir ./reports
```

The `shadowingvalue` command uses the same options as `shadowing` but provides more detailed analysis.

#### run example

Execute demonstration scenarios with sample data:

```bash
# List available examples
pins run example --help

# Run basic shadowing example
pins run example shadowing-basic

# Run example with table output
pins run example shadowing-basic --show table

# Run advanced example
pins run example shadowingvalue-basic

# Run example with export
pins run example shadowingvalue-basic --export json --export-dir ./reports

# Run example with multiple device groups
pins run example shadowing-multiple-dg --device-groups "Example 1" "Example 2"
```

**Available Examples:**

- `shadowing-basic` - Basic shadowing detection demonstration
- `shadowing-multiple-dg` - Multiple device group analysis
- `shadowingvalue-basic` - Advanced shadowing analysis with table output
- `shadowingvalue-with-export` - Advanced analysis with JSON export

## Configuration

### Environment Variables

You can set connection parameters using environment variables:

```bash
export PINS_PANORAMA_HOSTNAME=panorama.company.com
export PINS_PANORAMA_USERNAME=admin
export PINS_PANORAMA_PASSWORD=your_password
```

### Configuration File

Create a YAML configuration file to specify connection and analysis parameters:

```yaml
panorama:
    hostname: panorama.company.com
    username: admin
    password: your_password
    api_version: v11.1
    verify_ssl: false

analysis:
    device_groups:
        - Production
        - DMZ

output:
    show: [table]
    export: [html, json]
    export_dir: ./reports
```

Use the configuration file:

```bash
pins run shadowing --config config.yaml
```

## Output Formats

### Show Formats

**text** (default)
: Human-readable text output with basic formatting

**table**
: Structured table format for better readability

**json**
: Machine-readable JSON format

### Export Formats

**html**
: Interactive HTML report with styling and navigation

**json**
: Structured JSON data suitable for further processing

**csv**
: Comma-separated values for spreadsheet analysis

## Examples Workflow

### Getting Started

1. **Explore available scenarios:**

    ```bash
    pins list
    ```

2. **Try sample data:**

    ```bash
    pins run example shadowing-basic
    ```

3. **Connect to your Panorama:**
    ```bash
    pins run shadowing --panorama-hostname your-panorama.com \
         --panorama-username admin \
         --device-groups "Production"
    ```

### Production Usage

1. **Create a configuration file** with your Panorama details
2. **Run analysis regularly:**
    ```bash
    pins run shadowing --config production.yaml --export html json
    ```
3. **Review reports** in the export directory

### Advanced Analysis

Use the `shadowingvalue` command for more detailed analysis:

```bash
pins run shadowingvalue --config production.yaml \
     --show table \
     --export html --export-dir ./advanced-reports
```

## Best Practices

1. **Use configuration files** instead of command-line passwords
2. **Store sensitive data in environment variables**
3. **Export to multiple formats** for different audiences
4. **Analyze multiple device groups** together for comprehensive coverage
5. **Run examples first** to understand output formats and features

## Understanding Output Formats

        pass

````

## Understanding Output Formats

Policy Inspector supports multiple output formats for different needs:

### Show Formats

**text** (default)
: Human-readable text output with detailed explanations

**table**
: Structured table format ideal for terminal viewing

**json**
: Machine-readable JSON format for automation

Example usage:
```bash
# Default text output
pins run shadowing --config config.yaml

# Table format for better readability
pins run shadowingvalue --config config.yaml --show table

# JSON format for scripting
pins run shadowing --config config.yaml --show json

# Multiple formats simultaneously
pins run shadowingvalue --config config.yaml --show table json
````

### Export Formats

**html**
: Interactive HTML reports with styling and navigation

**json**
: Structured JSON data for further processing

**csv**
: Comma-separated values for spreadsheet analysis

Example usage:

```bash
# HTML report for sharing
pins run shadowingvalue --config config.yaml --export html --export-dir ./reports

# JSON export for automation
pins run shadowing --config config.yaml --export json --export-dir ./data

# CSV for spreadsheet analysis
pins run shadowingvalue --config config.yaml --export csv --export-dir ./analysis

# Multiple export formats
pins run shadowingvalue --config config.yaml --export html json csv --export-dir ./comprehensive
```

## Scenario Types

Policy Inspector currently provides two main analysis scenarios:

### Basic Shadowing (`shadowing`)

Standard shadowing detection that identifies rules that will never trigger:

```bash
pins run shadowing --config config.yaml
```

### Advanced Shadowing (`shadowingvalue`)

Enhanced analysis with more detailed output and sophisticated detection:

```bash
pins run shadowingvalue --config config.yaml --show table
```

### Working with Examples

Built-in examples help you understand the tool and test configurations:

```bash
# List available examples
pins run example --help

# Basic shadowing demonstration
pins run example shadowing-basic

# Advanced analysis with table output
pins run example shadowingvalue-basic --show table

# Multiple device groups example
pins run example shadowing-multiple-dg
```

## Common Workflow Patterns

### Development Workflow

```bash
# 1. Start with examples
pins run example shadowing-basic

# 2. Test your configuration
pins run example shadowingvalue-basic --config your-config.yaml

# 3. Run actual analysis
pins run shadowingvalue --config your-config.yaml
```

### Production Workflow

```bash
# 1. Create secure configuration with environment variables
export PINS_PANORAMA_HOSTNAME=panorama.company.com
export PINS_PANORAMA_USERNAME=admin
export PINS_PANORAMA_PASSWORD=secure_password

# 2. Run comprehensive analysis
pins run shadowingvalue --config production.yaml \
     --export html json --export-dir ./production-reports

# 3. Review reports and take action
```

### Automation Workflow

```bash
# 1. Automated daily analysis
pins run shadowingvalue --config automated.yaml \
     --export json --export-dir ./daily-$(date +%Y%m%d)

# 2. Check for critical issues in CI/CD
pins run shadowing --config ci-validation.yaml \
     --export json --export-dir ./ci-reports

# 3. Generate weekly summary reports
pins run shadowingvalue --config weekly-summary.yaml \
     --export html --export-dir ./weekly-reports
```

## Troubleshooting

### Common Issues

1. **Configuration Problems**

    ```bash
    # Test with examples first
    pins run example shadowing-basic --config your-config.yaml

    # Check command syntax
    pins run shadowing --help
    ```

2. **Connection Issues**

    ```bash
    # Verify with built-in examples
    pins list
    pins run example shadowingvalue-basic

    # Check SSL settings
    # Set verify_ssl: false in config for testing
    ```

3. **Output Issues**

    ```bash
    # Try different output formats
    pins run example shadowingvalue-basic --show table
    pins run example shadowingvalue-basic --show json

    # Check export directory permissions
    pins run example shadowingvalue-basic --export html --export-dir ./test
    ```

### Debug Mode

Use examples to debug and verify functionality:

```bash
# Test all available examples
pins run example shadowing-basic
pins run example shadowingvalue-basic --show table
pins run example shadowing-multiple-dg
```

## Best Practices

1. **Start Simple**: Always begin with built-in examples
2. **Use Configuration Files**: Store connection details and preferences in YAML files
3. **Secure Credentials**: Use environment variables for sensitive data
4. **Export Multiple Formats**: Generate both human-readable and machine-readable outputs
5. **Regular Analysis**: Schedule periodic security policy reviews
6. **Test Configurations**: Validate settings with examples before production use

## Next Steps

- {doc}`configuration` - Detailed configuration reference
- {doc}`../examples/basic-usage` - Practical usage examples
- {doc}`../examples/advanced-scenarios` - Advanced usage patterns
- {doc}`../examples/custom-filters` - Configuration examples
