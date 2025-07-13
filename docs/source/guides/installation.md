# Installation

Policy Inspector can be installed using pip or from source.

## Requirements

**System Requirements**
: Python 3.10 or higher  
: Network access to Palo Alto Panorama  
: Valid Panorama credentials

**Dependencies**
: pydantic >= 2.10.6  
: click >= 8.1.8  
: rich-click >= 1.8.7  
: requests >= 2.32.3  
: jinja2 >= 3.1.6

## Installation Methods

### Using pip (Recommended)

```bash
pip install policy-inspector
```

### Using Poetry

If you're using Poetry for dependency management:

```bash
poetry add policy-inspector
```

### Development Installation

For development or contributing to the project:

```bash
# Clone the repository
git clone https://github.com/your-org/policy-inspector.git
cd policy-inspector

# Install with Poetry
poetry install

# Or install with pip in development mode
pip install -e .
```

## Verification

Verify the installation by running:

```bash
pins --version
```

You should see output similar to:

```
Policy Inspector version 0.2.1
```

## Next Steps

- {doc}`quick-start` - Learn basic usage
- {doc}`configuration` - Set up your configuration
- {doc}`usage` - Explore advanced features
