# Configuration

Policy Inspector supports multiple ways to configure settings: files, environment variables, and command-line options.

## Quick Setup

### Basic Config File

Create `config.yaml` with your Panorama details:

```yaml
panorama:
    hostname: panorama.company.com
    username: admin
    verify_ssl: false
# Run with: pins run shadowing --config config.yaml
```

### Environment Variables

Set credentials without files:

```bash
export PINS_PANORAMA_HOSTNAME=panorama.company.com
export PINS_PANORAMA_USERNAME=admin
export PINS_PANORAMA_PASSWORD=your-password
```

## Configuration File

### Complete Example

Here's the full configuration format from {download}`config.example.yaml <../../../config.example.yaml>`:

```{literalinclude} ../../../config.example.yaml
:language: yaml
```

### File Locations

Policy Inspector searches for config files in this order:

1. `--config filename.yaml` (command line)
2. `./config.yaml` (current directory)
3. `~/.policy-inspector/config.yaml` (user home)
4. `/etc/policy-inspector/config.yaml` (system)

## Environment Variables

Set any option using `PINS_` prefix:

```bash
export PINS_PANORAMA_HOSTNAME=panorama.company.com
export PINS_PANORAMA_USERNAME=admin
export PINS_PANORAMA_PASSWORD=secret
```

## Command Line Options

Override any setting on the command line:

```bash
pins run shadowing --panorama-hostname panorama.company.com \
  --panorama-username admin --device-groups "Production"
```

## Priority Order

Settings are applied in this order (later overrides earlier):

1. Configuration file
2. Environment variables
3. Command line options

## Security Tips

**Keep credentials secure:**

- Use environment variables for passwords
- Set `verify_ssl: true` for production
- Limit config file permissions: `chmod 600 config.yaml`

**Example secure setup:**

```yaml
panorama:
    hostname: panorama.company.com
    username: admin
    verify_ssl: true
    # password via PINS_PANORAMA_PASSWORD env var
```

## Test Configuration

Validate your setup works:

```bash
# Test connection only
pins run example shadowing-basic

# Test with your Panorama
pins run shadowing --device-groups "test-group"
```
