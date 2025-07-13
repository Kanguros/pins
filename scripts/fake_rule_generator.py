# ruff: noqa: N803 FBT002
import random
from collections.abc import Iterator
from ipaddress import IPv4Network

import rich

from policy_inspector.model.base import AnyObj, AppDefault
from policy_inspector.model.security_rule import SecurityRule

ACTIONS = ["allow"] * 95 + ["deny"] * 5
ZONES = [
    "internal",
    "external",
    "dmz",
    "guest",
    "management",
    "public",
    "private",
    "sales",
    "engineering",
    "support",
    "testing",
    "development",
    "production",
]
SERVICES = [
    "http",
    "https",
    "ftp",
    "ssh",
    "dns",
    "smtp",
    "pop3",
    "imap",
    "rdp",
    "snmp",
    "telnet",
    "ldap",
    "nfs",
    "smb",
    "sql",
    "vpn",
    "sip",
    "tftp",
    "icmp",
]
APPLICATIONS = [
    "web-browsing",
    "email",
    "file-transfer",
    "remote-access",
    "database",
    "streaming-media",
    "voip",
    "gaming",
    "social-networking",
    "cloud-storage",
    "collaboration",
    "e-commerce",
    "news",
    "search-engine",
    "advertising",
    "analytics",
    "cdn",
    "content-sharing",
    "dev-tools",
    "finance",
]

ADDRESS_OBJECTS = [
    "srv-web01",
    "srv-db01",
    "srv-app01",
    "srv-mail01",
    "srv-backup01",
    "client-subnet1",
    "client-subnet2",
    "vpn-clients",
    "branch-office1",
    "branch-office2",
]
ADDRESS_GROUPS = [
    "all-servers",
    "internal-networks",
    "trusted-networks",
    "external-services",
]


def random_ip_network() -> str:
    """Generate a random IPv4 network."""
    return str(
        IPv4Network(
            (random.randint(0, 2**32 - 1), random.randint(8, 24)),
            strict=False,
        ),
    )


def random_selection(
    options: list[str],
    allow_AnyObj: bool = True,  # noqa: FBT001
) -> set[str] | str:
    """Randomly select a subset from options or return 'AnyObj'."""
    if allow_AnyObj and random.random() < 0.1:
        return {AnyObj}
    return set(random.sample(options, random.randint(1, min(3, len(options)))))


def random_address_selection(exclude: set[str] = None) -> set[str] | str:
    choices = (
        ADDRESS_OBJECTS
        + ADDRESS_GROUPS
        + [random_ip_network() for _ in range(50)]
    )
    selection = random_selection(choices)
    if exclude and selection == exclude:
        return random_address_selection(exclude)

    return selection


def random_zone_selection(exclude: set[str] = None) -> set[str] | str:
    selection = random_selection(ZONES)
    if exclude and selection == exclude:
        return random_zone_selection(exclude)
    return selection


def generate_security_rule(rule_id: int):
    src_zone = random_zone_selection()
    dst_zone = random_zone_selection(exclude=src_zone)
    src_addresses = random_address_selection()
    dst_addresses = random_address_selection(exclude=src_addresses)

    applications = random_selection(APPLICATIONS)
    services = (
        {AppDefault} if applications != {AnyObj} else random_selection(SERVICES)
    )

    return SecurityRule(
        name=f"rule_{rule_id}",
        action=random.choice(ACTIONS),
        source_zones=src_zone,
        destination_zones=dst_zone,
        source_addresses=src_addresses,
        destination_addresses=dst_addresses,
        applications=applications,
        services=services,
        category={AnyObj},
    )


def generate_security_rules(count: int) -> Iterator[SecurityRule]:
    """Generate a list of random security rules."""
    for i in range(1, count + 1):
        yield generate_security_rule(i)


if __name__ == "__main__":
    for fake_rule in generate_security_rules(10):
        rich.print(fake_rule)
