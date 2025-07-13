# Configuration

Policy Inspector supports multiple configuration methods to make it easy to use in different environments.

## Configuration Files

### YAML Configuration

The recommended configuration format is YAML. Create a `config.yaml` file:

```yaml
# Panorama connection settings
panorama:
    host: panorama.company.com
    username: admin
    password: secure-password
    port: 443
    verify_ssl: true
    timeout: 30

# Device groups to analyze
device_groups:
    - Production
    - Staging
    - Development

# Analysis settings
analysis:
    resolve_addresses: true
    max_concurrent_requests: 10
    cache_timeout: 300

# Output settings
output:
    format: json
    verbose: false
    show_progress: true

# Filtering options
filters:
    exclude_disabled: true
    exclude_tags:
        - "maintenance"
        - "temp"
    include_zones:
        - "trust"
        - "untrust"
        - "dmz"

# Scenarios to run
scenarios:
    shadowing:
        enabled: true
        check_overlap: true
        resolve_fqdns: true
```

### Configuration File Locations

Policy Inspector searches for configuration files in the following order:

1. File specified by `--config` option
2. `./config.yaml` (current directory)
3. `~/.policy-inspector/config.yaml` (user home)
4. `/etc/policy-inspector/config.yaml` (system-wide)

## Environment Variables

All configuration options can be set using environment variables with the `PINS_` prefix:

```bash
# Connection settings
export PINS_PANORAMA_HOST=panorama.company.com
export PINS_PANORAMA_USERNAME=admin
export PINS_PANORAMA_PASSWORD=secure-password

# Analysis settings
export PINS_DEVICE_GROUPS=Production,Staging
export PINS_RESOLVE_ADDRESSES=true
export PINS_MAX_CONCURRENT_REQUESTS=10

# Output settings
export PINS_OUTPUT_FORMAT=json
export PINS_OUTPUT_VERBOSE=false
```

## Command Line Options

All settings can be overridden using command-line options:

```bash
pins --panorama-host panorama.company.com \
     --username admin \
     --device-group "Production" \
     --output-format json \
     --verbose \
     show shadowing
```

## Priority Order

Configuration values are applied in the following priority order (highest to lowest):

1. Command-line options
2. Environment variables
3. Configuration file
4. Default values

## Secure Credential Management

### Using Environment Variables

```bash
# Set credentials securely
read -s PINS_PANORAMA_PASSWORD
export PINS_PANORAMA_PASSWORD
```

### Using External Secret Managers

Policy Inspector can integrate with external secret managers:

```yaml
panorama:
    host: panorama.company.com
    username: admin
    password_source:
        type: env
        key: PANORAMA_PASSWORD
```

### API Key Authentication

If your Panorama supports API key authentication:

```yaml
panorama:
    host: panorama.company.com
    api_key_source:
        type: env
        key: PANORAMA_API_KEY
```

## Advanced Configuration

### Custom Filters

Define reusable filters in your configuration:

```yaml
filters:
    production_rules:
        include_zones: ["trust", "untrust"]
        exclude_tags: ["temp", "test"]
        include_enabled_only: true

    security_review:
        include_any_source: true
        include_any_destination: true
        min_risk_level: medium
```

Use custom filters:

```bash
pins --filter production_rules show shadowing
```

### Scenario Configuration

Configure built-in scenarios:

```yaml
scenarios:
    shadowing:
        enabled: true
        algorithms:
            - overlap_detection
            - subnet_analysis
            - port_range_check
        output:
            include_suggestions: true
            group_by_severity: true
```

### Output Templates

Customize output formats:

```yaml
output:
    templates:
        html:
            template_file: custom_report.html
            include_charts: true
            theme: dark

        json:
            pretty_print: true
            include_metadata: true
```

## Validation

Validate your configuration:

```bash
pins config validate
```

Show current configuration:

```bash
pins config show
```

## Next Steps

- {doc}`usage` - Learn about advanced usage patterns
- {doc}`../examples/basic-usage` - See configuration examples
