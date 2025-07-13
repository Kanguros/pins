# Quick Start

This guide will get you started with Policy Inspector in just a few minutes.

## Installation

Install Policy Inspector using pip:

```bash
pip install policy-inspector
```

## Basic Usage

### 1. Explore Available Scenarios

First, see what scenarios are available:

```bash
pins list
```

### 2. Try Built-in Examples

Start with built-in examples to verify installation:

```bash
# Run basic shadowing example
pins run example shadowing-basic

# Run advanced example with table output
pins run example shadowingvalue-basic --show table
```

### 3. Connect to Your Panorama

Once examples work, connect to your actual Panorama:

```bash
# Basic shadowing analysis
pins run shadowing --panorama-hostname your-panorama.company.com \
     --panorama-username admin \
     --device-groups "Production"

# Advanced analysis with table output
pins run shadowingvalue --panorama-hostname your-panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" --show table
```

### 4. Generate Reports

Export results to files:

```bash
# HTML report
pins run shadowing --panorama-hostname your-panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" \
     --export html --export-dir ./reports

# Multiple formats
pins run shadowingvalue --panorama-hostname your-panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" \
     --export html json --export-dir ./reports
```

## Authentication Options

### Environment Variables

Set credentials using environment variables:

```bash
export PINS_PANORAMA_HOSTNAME=your-panorama.company.com
export PINS_PANORAMA_USERNAME=admin
export PINS_PANORAMA_PASSWORD=your-password

# Now you can run commands without explicit connection parameters
pins run shadowing --device-groups "Production"
```

### Configuration File

Create a configuration file `config.yaml`:

```yaml
panorama:
    hostname: your-panorama.company.com
    username: admin
    password: your-password
    verify_ssl: false

analysis:
    device_groups:
        - Production
        - Staging

output:
    show: [table]
    export: [html]
    export_dir: ./reports
```

Then use:

```bash
pins run shadowing --config config.yaml
pins run shadowingvalue --config config.yaml
```

```bash
pins --config config.yaml show shadowing
```

## Common Use Cases

### Finding Shadowed Rules

```bash
# Basic shadowing detection
pins run shadowing --config config.yaml

# Advanced analysis with table output
pins run shadowingvalue --config config.yaml --show table

# Export to multiple formats
pins run shadowingvalue --config config.yaml --export json html --export-dir ./reports
```

### Analyzing Multiple Device Groups

```bash
# Analyze multiple device groups
pins run shadowing --panorama-hostname your-panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" "Staging" "Development"

# Using configuration file with multiple groups
pins run shadowingvalue --config multi-env-config.yaml
```

### Working with Examples

```bash
# See all available examples
pins run example --help

# Try different examples
pins run example shadowing-basic
pins run example shadowingvalue-basic --show table
pins run example shadowing-multiple-dg
# Export examples with different formats
pins run example shadowingvalue-basic --export json --export-dir ./examples
```

## Getting Help

```bash
# Get help for main commands
pins --help
pins list
pins run --help

# Get help for specific scenarios
pins run shadowing --help
pins run shadowingvalue --help
pins run example --help
```

## Next Steps

- {doc}`configuration` - Learn about configuration options
- {doc}`usage` - Explore advanced features
- {doc}`../examples/basic-usage` - See more examples
