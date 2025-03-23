# Notes


## Scenarios

A scenario is a set of checks that evaluate firewall rules against 
specific issues or configurations. Each scenario is designed to identify particular problem.

### Available Scenarios

#### 1. Basic Shadowing

This scenario identifies when a rule is completely shadowed by a
preceding rule. Shadowing occurs when a rule will never be matched
because a rule earlier in the processing order would always match
first.

```bash
pi run shadowing security_rules.json
```

This scenario checks if two rules match on:

- Action (allow/deny/monitor)
- Source and destination zones
- Source and destination addresses
- Applications
- Services (ports)

When all checks pass between a rule and a preceding rule, the later
rule is reported as shadowed.

#### 2. Complex Shadowing

This scenario performs more thorough analysis by resolving IP
addresses in your rules and comparing actual network ranges. This
helps identify partial or complete shadowing at the IP address level.


```bash
pi run complex_shadowing security_rules.json address_groups.json address_objects.json
```

This scenario needs:

- Security rules
- Address groups definitions
- Address objects definitions

It provides more precise analysis by checking if IP subnets in later
rules are completely contained within IP subnets of earlier rules.

### Understanding Scenario Results

When you run a scenario, Policy Inspector will:

1. Load your security rules (and address objects if needed)
2. Compare each rule against all preceding rules
3. Output which rules are shadowed, and by which preceding rules
4. Provide detailed information about why a rule is shadowed

### Example Workflow

A typical workflow for a network engineer might be:

1. Export your firewall security rules to JSON format
2. Run the basic shadowing check:
   ```bash
   pi run shadowing my_firewall_rules.json
   ```
3. Review which rules are shadowed
4. For more precise analysis, export address groups and objects, then
   run:
   ```bash
   pi run complex_shadowing my_firewall_rules.json my_address_groups.json my_address_objects.json
   ```
5. Use the results to clean up redundant rules in your firewall policy

This approach helps maintain cleaner, more efficient firewall
configurations and improves security by reducing configuration
complexity.

---
Answer from Perplexity: pplx.ai/share