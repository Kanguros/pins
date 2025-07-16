# Quick Start

Get started with Policy Inspector in 3 simple steps.

## 1. Install

```bash
pip install policy-inspector
```

## 2. Try an Example

Test installation with built-in sample data:

```bash
pins run example shadowing-basic
```

## 3. Connect to Panorama

Replace with your Panorama details:

```bash
pins run shadowing \
  --panorama-hostname your-panorama.company.com \
  --panorama-username admin \
  --device-groups "Production"
```

Enter your password when prompted.

## What's Next?

- **View results differently**: Add `--show table` for table format
- **Save reports**: Add `--export html --export-dir ./reports` 
- **Use config files**: See {doc}`configuration` for easier credential management
- **Advanced analysis**: Try `pins run shadowingvalue` for deeper inspection

## Getting Help

```bash
pins --help                    # Main commands
pins run --help               # Available scenarios  
pins run shadowing --help     # Command options
```
