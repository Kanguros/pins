# Policy Inspector Documentation

**Policy Inspector for Palo Alto Networks** - Analyze firewall security policies and detect shadowed rules.

**Policy Inspector** is a command-line tool that connects directly to your Palo Alto Panorama to analyze firewall security policies in real-time. It identifies shadowed rules, validates configurations, and provides comprehensive security policy insights.

## Key Features

- **🔍 Shadowing Detection**: Identifies rules that will never trigger due to preceding rules
- **🌐 Direct API Integration**: Connects to Panorama via REST API - no manual exports needed
- **🔧 Multi-Device Group Support**: Analyze multiple device groups simultaneously
- **📊 Advanced Analysis**: Resolves IP addresses for precise shadowing detection
- **📈 Multiple Output Formats**: Text, HTML, JSON, and CSV reporting
- **🔌 Extensible Framework**: Easy to add custom scenarios and checks

## Documentation Contents

```{toctree}
:maxdepth: 2
:caption: User Guide

guides/installation
guides/quick-start
guides/configuration
guides/usage
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/index
```

```{toctree}
:maxdepth: 2
:caption: Examples

examples/basic-usage
examples/advanced-scenarios
examples/custom-filters
```

```{toctree}
:maxdepth: 1
:caption: Development

development/contributing
development/testing
```

## Quick Start

Install Policy Inspector using pip:

```bash
pip install policy-inspector
```

Basic usage:

```bash
# List available scenarios
pins list

# Try the demo with sample data
pins run example shadowing-basic

# Analyze a device group for shadowed rules
pins run shadowing --panorama-hostname your-panorama.company.com \
     --panorama-username admin \
     --device-groups "Production"

# Export results to HTML report
pins run shadowing --panorama-hostname your-panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" \
     --export html --export-dir ./reports
```

## Indices and Tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
