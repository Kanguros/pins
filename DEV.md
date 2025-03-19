# Development

## Package tree

```shell
│   .gitignore
│   .pre-commit-config.yaml        
│   LICENSE
│   poetry.lock
│   pyproject.toml
│   README.md
│
├───policy_inspector
│   │   check.py
│   │   evaluate.py
│   │   models.py
│   │   resolve.py
│   │   utils.py
│   │   __init__.py
│   │   __main__.py
│   │
│   ├───tests
│   │   │   conftest.py
│   │   │   test_cli.py
│   │   │   test_models.py
│   │   │   _test_resolver.py
│   │   │   __init__
│   │   │
│   │   ├───data
│             address_groups.json
│             address_objects.json
│             security_rules.json
```

## Fake rules

```json
[
  {
    "@device-group": "devicegroup-7",
    "@location": "device-group",
    "@name": "rule-example1",
    "action": "allow",
    "application": {
      "member": [
        "email-collaboration-apps"
      ]
    },
    "category": {
      "member": [
        "any"
      ]
    },
    "destination": {
      "member": [
        "any"
      ]
    },
    "from": {
      "member": [
        "zone-edge1"
      ]
    },
    "hip-profiles": {
      "member": [
        "any"
      ]
    },
    "service": {
      "member": [
        "application-default"
      ]
    },
    "source": {
      "member": [
        "any"
      ]
    },
    "source-user": {
      "member": [
        "any"
      ]
    },
    "to": {
      "member": [
        "any"
      ]
    }
  },
  {
    "@location": "device-group",
    "@name": "rule-example2",
    "@device-group": "devicegroup-7",
    "action": "allow",
    "application": {
      "member": [
        "email-collaboration-apps"
      ]
    },
    "category": {
      "member": [
        "any"
      ]
    },
    "destination": {
      "member": [
        "cloud_log_server"
      ]
    },
    "from": {
      "member": [
        "zone-edge1"
      ]
    },
    "hip-profiles": {
      "member": [
        "any"
      ]
    },
    "service": {
      "member": [
        "application-default"
      ]
    },
    "source": {
      "member": [
        "Main_Linux_Server"
      ]
    },
    "source-user": {
      "member": [
        "any"
      ]
    },
    "to": {
      "member": [
        "any"
      ]
    }
  },
  {
    "@device-group": "devicegroup-7",
    "@location": "device-group",
    "@name": "rule3-allow-dns",
    "action": "allow",
    "application": {
      "member": [
        "dns"
      ]
    },
    "category": {
      "member": [
        "any"
      ]
    },
    "destination": {
      "member": [
        "LogServers"
      ]
    },
    "from": {
      "member": [
        "any"
      ]
    },
    "hip-profiles": {
      "member": [
        "any"
      ]
    },
    "log-setting": "log-forwarding-LS",
    "log-start": "yes",
    "service": {
      "member": [
        "application-default"
      ]
    },
    "source": {
      "member": [
        "any"
      ]
    },
    "source-user": {
      "member": [
        "any"
      ]
    },
    "target": {
      "negate": "no"
    },
    "to": {
      "member": [
        "any"
      ]
    }
  }
]

```