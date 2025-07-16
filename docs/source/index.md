# Policy Inspector Documentation

**Policy Inspector** - Analyze Palo Alto firewall policies and detect shadowed rules.

A command-line tool that connects to Panorama to identify security rules that will never trigger due to preceding rules with broader conditions.

## Key Features

- **🔍 Shadowing Detection**: Find rules that never trigger  
- **🌐 Direct API Integration**: Connect to Panorama - no exports needed
- ** Advanced Analysis**: Resolve IP addresses for precise detection
- **📈 Multiple Output Formats**: Text, table, HTML, JSON, and CSV
- **� Multi-Device Groups**: Analyze multiple groups simultaneously

## Quick Example

```bash
# Install
pip install policy-inspector

# Try with sample data
pins run example shadowing-basic

# Connect to your Panorama
pins run shadowing --panorama-hostname panorama.company.com \
  --panorama-username admin --device-groups "Production"
```

## Documentation

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
:caption: Examples

examples/basic-usage
examples/advanced-scenarios
examples/custom-filters
```

```{toctree}
:maxdepth: 2
:caption: Reference

api/index
cli/index
```

```{toctree}
:maxdepth: 1
:caption: Development

development/contributing
development/testing
```
