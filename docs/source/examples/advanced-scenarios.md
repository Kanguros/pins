# Advanced Scenarios

This guide covers advanced usage patterns and real-world scenarios for Policy Inspector.

## Advanced Shadowing Analysis

Policy Inspector provides two main analysis scenarios:

1. **Basic Shadowing** (`pins run shadowing`) - Standard shadowing detection
2. **Advanced Shadowing** (`pins run shadowingvalue`) - Enhanced analysis with more detailed output

### Enhanced Analysis with shadowingvalue

The `shadowingvalue` scenario provides more sophisticated analysis:

```bash
# Advanced shadowing analysis with table output
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production" --show table

# Multiple output formats
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin --device-groups "Production" \
     --show table --export json html --export-dir ./reports

# Configuration file approach
pins run shadowingvalue --config config.yaml
```

### Multi-Device Group Analysis

Analyze multiple device groups simultaneously:

```bash
# Analyze multiple environments
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Production" "Staging" "DMZ" \
     --show table --export html --export-dir ./multi-env-reports

# Using configuration file for complex setups
pins run shadowing --config multi-env-config.yaml
```

Configuration file example:

```yaml
panorama:
    hostname: panorama.company.com
    username: admin
    password: ${PANORAMA_PASSWORD}
    api_version: v11.1
    verify_ssl: false

analysis:
    device_groups:
        - Production
        - Staging
        - DMZ
        - Internal

output:
    show: [table]
    export: [html, json]
    export_dir: ./comprehensive-reports
```

## Real-World Enterprise Scenarios

### Scenario 1: Security Audit Preparation

```bash
# Comprehensive analysis for security audit
pins run shadowingvalue --config audit-config.yaml \
     --export html json --export-dir ./audit-reports

# Generate reports for multiple environments
for env in Production Staging Development; do
    pins run shadowingvalue --panorama-hostname panorama.company.com \
         --panorama-username admin \
         --device-groups "$env" \
         --export html --export-dir "./audit-reports/$env"
done
```

### Scenario 2: Policy Migration Assessment

```bash
# Analyze current state before migration
pins run shadowingvalue --config current-state.yaml \
     --export json --export-dir ./migration-baseline

# Compare different device groups
pins run shadowing --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Legacy-Firewall" \
     --export json --export-dir ./legacy-analysis

pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "New-Firewall" \
     --export json --export-dir ./new-analysis
```

### Scenario 3: Regular Compliance Monitoring

```bash
#!/bin/bash
# Monthly compliance check script

DATE=$(date +%Y-%m)
REPORT_DIR="compliance-reports/$DATE"
mkdir -p "$REPORT_DIR"

# Analyze all critical environments
for env in Production DMZ External; do
    echo "Analyzing $env environment..."

    pins run shadowingvalue --config compliance.yaml \
         --device-groups "$env" \
         --export html json --export-dir "$REPORT_DIR/$env"

    if [ $? -ne 0 ]; then
        echo "WARNING: Analysis failed for $env"
    fi
done

# Generate summary
echo "Compliance analysis completed for $DATE"
echo "Reports available in: $REPORT_DIR"
```

## Automation and Integration

### CI/CD Integration

```bash
#!/bin/bash
# policy-validation.sh - CI/CD pipeline script

set -euo pipefail

echo "Starting policy validation..."

# Run analysis
pins run shadowingvalue --config ci-config.yaml \
     --export json --export-dir ./ci-reports

# Check if results file exists
if [ ! -f "./ci-reports/shadowingvalue_results.json" ]; then
    echo "ERROR: Analysis failed - no results generated"
    exit 1
fi

echo "Policy validation completed successfully"
exit 0
```

### Scheduled Analysis

```bash
#!/bin/bash
# weekly-policy-check.sh - Cron job script

# Run weekly comprehensive analysis
WEEK=$(date +%Y-W%U)
REPORT_DIR="/var/reports/policy-inspector/$WEEK"
mkdir -p "$REPORT_DIR"

# Production analysis
pins run shadowingvalue --config /etc/policy-inspector/production.yaml \
     --export html json --export-dir "$REPORT_DIR/production"

# Staging analysis
pins run shadowing --config /etc/policy-inspector/staging.yaml \
     --export html json --export-dir "$REPORT_DIR/staging"

# Send notification
echo "Weekly policy analysis completed: $REPORT_DIR" | \
mail -s "Policy Inspector Weekly Report" security-team@company.com
```

## Best Practices for Advanced Usage

1. **Start Small**: Begin with single device groups before scaling
2. **Use Configuration Files**: Maintain consistent settings across runs
3. **Export Multiple Formats**: Generate both human-readable (HTML) and machine-readable (JSON) outputs
4. **Regular Analysis**: Schedule periodic checks for ongoing compliance
5. **Test First**: Use built-in examples to verify setup before production use

## Example Workflows

### Daily Operations

```bash
# Quick morning check
pins run example shadowing-basic

# Production analysis
pins run shadowingvalue --config daily-check.yaml

# Generate reports for management
pins run shadowingvalue --config management-report.yaml \
     --export html --export-dir ./daily-reports/$(date +%Y%m%d)
```

### Incident Response

```bash
# Emergency analysis after rule changes
pins run shadowingvalue --panorama-hostname panorama.company.com \
     --panorama-username admin \
     --device-groups "Affected-Device-Group" \
     --show table --export html json --export-dir ./incident-$(date +%Y%m%d-%H%M)
```

## Next Steps

- {doc}`custom-filters` - Learn about filtering and output customization
- {doc}`../guides/configuration` - Advanced configuration options
- {doc}`basic-usage` - Return to basic usage patterns
