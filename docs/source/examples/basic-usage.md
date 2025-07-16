# Basic Usage Examples

Common Policy Inspector usage patterns with real examples.

## Try Built-in Examples

No credentials needed - perfect for testing:

```bash
# Basic shadowing detection
pins run example shadowing-basic

# Advanced analysis with table view
pins run example shadowingvalue-basic --show table

# Export results
pins run example shadowingvalue-basic --export json --export-dir ./reports
```

## Connect to Your Panorama

### Using Command Line

```bash
pins run shadowing \
  --panorama-hostname panorama.company.com \
  --panorama-username admin \
  --device-groups "Production"
```

### Using Environment Variables

Set credentials once:
```bash
export PINS_PANORAMA_HOSTNAME=panorama.company.com
export PINS_PANORAMA_USERNAME=admin
export PINS_PANORAMA_PASSWORD=your-password

# Now run without repeating credentials
pins run shadowing --device-groups "Production"
```

### Using Configuration File

Create `config.yaml` using the example from the project:

```{literalinclude} ../../../config.example.yaml
:language: yaml
:lines: 1-20
```

Then run:
```bash
pins run shadowing --config config.yaml
```

## Output Formats

### View Results

```bash
# Default text output
pins run example shadowing-basic

# Table format
pins run example shadowing-basic --show table

# Rich colored output  
pins run example shadowing-basic --show rich
```

### Export Results

```bash
# HTML report
pins run shadowing --config config.yaml --export html

# Multiple formats
pins run shadowingvalue --config config.yaml --export json csv html --export-dir ./reports
```

## Multiple Device Groups

Analyze several device groups at once:

```bash
pins run shadowing \
  --panorama-hostname panorama.company.com \
  --panorama-username admin \
  --device-groups "Production" "Staging" "Development"
```

## Common Workflows

### Security Review

1. Start with examples to verify setup
2. Run basic shadowing analysis
3. Use advanced analysis for detailed review
4. Export reports for documentation

```bash
# 1. Verify setup
pins run example shadowing-basic

# 2. Basic analysis
pins run shadowing --config config.yaml

# 3. Detailed analysis
pins run shadowingvalue --config config.yaml --show table

# 4. Generate reports
pins run shadowingvalue --config config.yaml --export html json --export-dir ./security-review
```

### Continuous Monitoring

Use in scripts for regular checks:

```bash
#!/bin/bash
# daily-security-check.sh

pins run shadowingvalue \
  --config /etc/policy-inspector/config.yaml \
  --export json \
  --export-dir "/var/log/security-checks/$(date +%Y-%m-%d)"
```

## Getting Help

```bash
pins --help                    # Main commands
pins run --help               # Available scenarios
pins run shadowing --help     # Specific scenario options
```
