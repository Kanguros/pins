# Basic Usage Examples

This page provides practical examples of using Policy Inspector for common tasks.

## Initial Setup

### Setting Up Credentials

The most secure way to provide credentials is through environment variables:

```bash
# Set up environment variables
export PINS_PANORAMA_HOSTNAME=panorama.company.com
export PINS_PANORAMA_USERNAME=admin

# Prompt for password securely
read -s PINS_PANORAMA_PASSWORD
export PINS_PANORAMA_PASSWORD
```

### Creating a Configuration File

Create a `config.yaml` file for repeated use:

```yaml
panorama:
    hostname: panorama.company.com
    username: admin
    password: ${PANORAMA_PASSWORD} # Reference environment variable

device_groups:
    - Production
    - Staging

output:
    format: json
    verbose: true
```

## Discovery and Exploration

### List Available Scenarios

```bash
# Show all available scenarios
pins list
```

### Explore Built-in Examples

```bash
# Show available examples
pins run example --help

# Run basic example
pins run example shadowing-basic

# Run example with different output format
pins run example shadowing-basic --show table
```

## Shadowing Analysis

### Basic Shadowing Detection

```bash
# Analyze using configuration file
pins run shadowing --config config.yaml

# Analyze specific device group
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production"

# Quick analysis with text output
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production" --show text
```

Example output:

```
Shadowing Analysis Results:
┌──────────────────────┬─────────────────────┬──────────┬────────────┐
│ Shadowed Rule        │ Shadowing Rule      │ Severity │ Reason     │
├──────────────────────┼─────────────────────┼──────────┼────────────┤
│ Allow-Web-Specific   │ Allow-Web-All       │ High     │ Subnet     │
│ Deny-FTP-Internal    │ Deny-All-Internal   │ Medium   │ Protocol   │
│ Allow-SSH-Mgmt       │ Allow-Any-Mgmt      │ Low      │ Port Range │
└──────────────────────┴─────────────────────┴──────────┴────────────┘

Total shadowed rules: 3
High severity: 1, Medium severity: 1, Low severity: 1
```

### Advanced Shadowing Analysis

```bash
# Verbose output with detailed explanations
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production" --show text

# Multiple device groups
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" "Staging" --show table

# With export to multiple formats
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production" \
     --show table --export json --export html --export-dir ./reports
```

## Report Generation

### HTML Reports

```bash
# Basic HTML report
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production" \
     --export html --export-dir ./reports

# Advanced analysis with HTML export
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production" \
     --export html --export-dir ./reports
```

### JSON Export

```bash
# Standard JSON output
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production" \
     --export json --export-dir ./reports

# Using examples for quick testing
pins run example shadowingvalue-basic --export json --export-dir ./reports
```

### Multiple Output Formats

```bash
# Generate both text display and file exports
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production" \
     --show table --export json --export html --export-dir ./reports

# Using configuration file
pins run shadowing --config config.yaml --export json --export html
```

## Multiple Device Groups

### Parallel Analysis

```bash
# Analyze multiple device groups
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" "Staging" "Development"

# Using configuration file with multiple device groups
pins run shadowing --config config.yaml

# Export results for multiple device groups
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" "Staging" \
     --export json --export html --export-dir ./reports
```

## Working with Configuration Files

### Using Configuration Files

Create reusable configuration files for your environment:

```yaml
# config.yaml
panorama:
    hostname: panorama.company.com
    username: admin
    password: ${PANORAMA_PASSWORD}

analysis:
    device_groups:
        - Production
        - Staging

output:
    show: [table]
    export: [json, html]
    export_dir: ./reports
```

Use the configuration:

```bash
# Analyze using configuration file
pins run shadowing --config config.yaml

# Override specific settings
pins run shadowingvalue --config config.yaml --show text
```

## Automation and Scripting

### Automated Reporting

```bash
#!/bin/bash
# Daily shadowing report script

DATE=$(date +%Y%m%d)
REPORT_DIR="reports/$DATE"

# Create report directory
mkdir -p "$REPORT_DIR"

# Generate reports for each environment
for env in Production Staging Development; do
    echo "Analyzing $env..."

    # HTML report
    pins run shadowing --config config.yaml \
         --device-groups "$env" \
         --export html --export-dir "$REPORT_DIR"

    # JSON for automation
    pins run shadowingvalue --config config.yaml \
         --device-groups "$env" \
         --export json --export-dir "$REPORT_DIR"
done

echo "Reports generated in $REPORT_DIR"
```

### CI/CD Integration

```bash
#!/bin/bash
# CI/CD pipeline script

# Run analysis and export to JSON
pins run shadowing --config config.yaml \
     --export json --export-dir .

# Check for high-severity issues (assuming JSON output structure)
if [ -f "shadowing_results.json" ]; then
    HIGH_SEVERITY=$(jq -r '.summary.high_severity_count // 0' shadowing_results.json)

    if [ "$HIGH_SEVERITY" -gt 0 ]; then
        echo "❌ Found $HIGH_SEVERITY high-severity shadowing issues"
        exit 1
    else
        echo "✅ No high-severity shadowing issues found"
    fi
else
    echo "❌ Analysis failed - no results file generated"
    exit 1
fi
```

### Example Integration Scripts

```bash
# Test scenario with examples first
pins run example shadowing-basic

# Validate configuration file
pins run shadowing --config config.yaml --help
```

## Best Practices

### Security Considerations

```bash
# Use environment variables for sensitive data
export PINS_PANORAMA_PASSWORD=your_password

# Verify SSL certificates in production
pins run shadowing --config config.yaml --panorama-verify-ssl

# Run examples to test functionality
pins run example shadowingvalue-basic --show table
```

### Multiple Device Groups

```bash
# Analyze multiple device groups simultaneously
pins run shadowing --config config.yaml \
     --device-groups "Production" "Staging" "DMZ"

# Use configuration file for consistent settings
pins run shadowingvalue --config config.yaml

# Export results for different environments
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" "Staging" \
     --export json html --export-dir ./reports
```

## Troubleshooting Common Issues

### Connection Issues

```bash
# Test with built-in examples first
pins run example shadowing-basic

# Check your configuration
pins run shadowing --config config.yaml --help

# Use examples to verify functionality
pins list
```

### Getting Help

```bash
# Get help for specific commands
pins --help
pins run --help
pins run shadowing --help
pins run example --help

# List available scenarios and examples
pins list

# Try built-in examples
pins run example shadowing-basic
pins run example shadowingvalue-basic --show table
```

### Common Solutions

```bash
# Start with examples to verify installation
pins run example shadowing-basic

# Use configuration files for complex setups
pins run shadowing --config config.yaml

# Check available output formats
pins run example shadowingvalue-basic --show table --export json
```

```

## Next Steps

- {doc}`advanced-scenarios` - Learn about advanced analysis scenarios
- {doc}`custom-filters` - Create custom filters for your environment
- {doc}`../guides/configuration` - Deep dive into configuration options
```
