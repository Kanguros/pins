import logging
from pathlib import Path
from textwrap import dedent
from typing import TypeVar

import rich_click as click
from click import ClickException
from rich_click import rich_config

from policy_inspector.connector.panorama import PanoramaConnector
from policy_inspector.loader import load_model, save_json
from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import AddressObject
from policy_inspector.model.base import MainModel
from policy_inspector.model.security_rule import SecurityRule
from policy_inspector.output.html_report import export_as_html
from policy_inspector.shadowing import Scenario, Shadowing, ShadowingByValue
from policy_inspector.utils import (
    Example,
    ExampleChoice,
    FilePath,
    config_logger,
    exclude_check_option,
    html_report,
    output_format_option,
    verbose_option,
)

config_logger()

click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.TEXT_MARKUP = "markdown"
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_METAVARS_COLUMN = True

logger = logging.getLogger(__name__)

ConcreteScenario = TypeVar("ConcreteScenario", bound="Scenario")


@click.group(no_args_is_help=True, add_help_option=True)
@verbose_option()
def main():
    """*PINS*
    as Policy Inspector
    """


@main.command("list")
@verbose_option()
def main_list() -> None:
    """List available Scenarios."""
    logger.info("")
    logger.info("-----------------------")
    logger.info("")
    for scenario in Scenario.get_available().values():
        logger.info(f"→ '{scenario.name}'")
        scenario_doc = scenario.__doc__
        if scenario_doc:
            doc = dedent(scenario_doc)
            logger.info(f"{doc}")
        for check in scenario.checks:
            logger.info(f"\t▶ '{check.__name__}'")
            doc = check.__doc__.replace("\n", "")
            logger.info(f"\t  {doc}")
        logger.info("")
        logger.info("-----------------------")
        logger.info("")


@main.command("pull")
@verbose_option()
@click.option(
    "-h",
    "--host",
    "hostname",
    nargs=1,
    type=click.STRING,
    help="Panorama hostname",
    required=True,
)
@click.option(
    "-pv",
    "--panos-version",
    "panos_version",
    nargs=1,
    type=click.STRING,
    help="PAN-OS version",
    default="v11.1",
    show_default=True,
)
@click.option(
    "-u",
    "--username",
    nargs=1,
    type=click.STRING,
    help="Panorama username",
    required=True,
)
@click.option(
    "-p",
    "--password",
    nargs=1,
    type=click.STRING,
    help="Panorama password",
    required=True,
)
@click.option(
    "-d",
    "--device-group",
    "device_groups",
    nargs=1,
    type=click.STRING,
    help="Name of the Device Group",
    required=True,
    multiple=True,
)
@click.option(
    "--ssl",
    "verify_ssl",
    nargs=1,
    help="SSL",
    default=False,
)
def main_pull(
    hostname: str,
    panos_version: str,
    username: str,
    password: str,
    device_groups: tuple[str],
    verify_ssl,
) -> None:
    """Pull Security Rules, Address Objects and Address Groups from Panorama for given Device Group."""
    get_data_from_panorama(
        hostname=hostname,
        username=username,
        password=password,
        device_groups=device_groups,
        api_version=panos_version,
        verify_ssl=verify_ssl,
    )


@main.group("run", no_args_is_help=True)
@verbose_option()
@rich_config(
    help_config={
        "style_argument": "bold yellow",
        "commands_panel_title": "Scenarios",
    }
)
def main_run():
    """Execute a Scenario.


    To see how it works, run one of the examples


    ```
    pins run example

    ```

    """


@main_run.command("config", no_args_is_help=True)
@click.argument("config_file_path", type=FilePath())
@verbose_option()
def run_config(config_file_path):
    pass


@main_run.command("shadowing", no_args_is_help=True)
@verbose_option()
@click.argument(
    "security_rules_path",
    required=True,
    type=FilePath(),
)
@exclude_check_option()
@output_format_option()
@html_report()
def run_shadowing(
    security_rules_path: Path,
    exclude_checks: tuple[str],
    display_formats: tuple[str],
    html_report: bool,
) -> None:
    process_scenario(
        Shadowing,
        (SecurityRule, security_rules_path),
        exclude_checks=exclude_checks,
        display_formats=display_formats,
        html_report=html_report,
    )


@main_run.command("shadowingvalue", no_args_is_help=True)
@verbose_option()
@click.argument(
    "security_rules_path",
    required=True,
    type=FilePath(),
)
@click.argument(
    "address_objects_path",
    required=True,
    type=FilePath(),
)
@click.argument(
    "address_groups_path",
    required=True,
    type=FilePath(),
)
@exclude_check_option()
@output_format_option()
@html_report()
def run_shadowingvalue(
    security_rules_path: Path,
    address_objects_path: Path,
    address_groups_path: Path,
    exclude_checks: tuple[str],
    display_formats: tuple[str],
    html_report: bool,
) -> None:
    process_scenario(
        ShadowingByValue,
        (SecurityRule, security_rules_path),
        (AddressObject, address_objects_path),
        (AddressGroup, address_groups_path),
        exclude_checks=exclude_checks,
        display_formats=display_formats,
        html_report=html_report,
    )


examples = [
    Example(
        name="1",
        args=[Path("1/policies.json")],
        cmd=run_shadowing,
    ),
    Example(
        name="2",
        args=[Path("2/policies.json")],
        cmd=run_shadowing,
    ),
    Example(
        name="3",
        args=[
            Path("1/policies.json"),
            Path("1/address_objects.json"),
            Path("1/address_groups.json"),
        ],
        cmd=run_shadowingvalue,
    ),
    Example(
        name="4",
        args=[
            Path("2/policies.json"),
            Path("2/address_objects.json"),
            Path("2/address_groups.json"),
        ],
        cmd=run_shadowingvalue,
    ),
]


@main_run.command("example", no_args_is_help=True)
@click.argument(
    "example",
    type=ExampleChoice(examples),
)
@verbose_option()
@exclude_check_option()
@output_format_option()
@html_report()
@click.pass_context
def run_example(
    ctx,
    example: Example,
    exclude_checks: tuple[str],
    display_formats: tuple[str],
    html_report: bool,
) -> None:
    """Run one of the examples."""
    logger.info(f"▶ Selected example: '{example.name}'")
    ctx.invoke(
        example.cmd.callback,
        *example.args,
        exclude_checks=exclude_checks,
        display_formats=display_formats,
        html_report=html_report,
    )


def get_data_from_panorama(
    hostname: str,
    username: str,
    password: str,
    api_version: str,
    device_groups: list[str],
    verify_ssl,
    continue_on_error: bool = True,
) -> dict[str, dict[str, Path]]:
    try:
        logger.info(f"↺ Connecting to Panorama at {hostname}")
        panorama = PanoramaConnector(
            hostname=hostname,
            username=username,
            password=password,
            api_version=api_version,
            verify_ssl=verify_ssl,
        )
        logger.info("✓ Successfully authenticated to Panorama")
    except Exception as ex:
        raise ClickException(str(ex)) from None

    logger.info("▶ Retrieving shared items")
    shared_address_objects = panorama.get_address_objects()
    shared_address_groups = panorama.get_address_groups()

    data = {}
    for device_group in device_groups:
        dg_files = {}
        try:
            logger.info(f"▶ Processing Device Group: '{device_group}'")

            prefix = f"{device_group.lower().replace(' ', '_')}_".strip()

            security_rules = panorama.get_security_rules(
                device_group=device_group
            )
            dg_files["security_rules"] = save_json(
                security_rules, f"{prefix}security_rules.json"
            )

            address_objects = panorama.get_address_objects(
                device_group=device_group
            )
            dg_files["address_objects"] = save_json(
                address_objects + shared_address_objects,
                f"{prefix}address_objects.json",
            )

            address_groups = panorama.get_address_groups(
                device_group=device_group
            )
            dg_files["address_groups"] = save_json(
                address_groups + shared_address_groups,
                f"{prefix}address_groups.json",
            )
            data[device_group] = dg_files
        except Exception as ex:
            if continue_on_error:
                logger.error(f"Error occur '{device_group}' {ex}.")
                continue
            raise ClickException(str(ex)) from None
    logger.info("✓ All data successfully pulled and saved")
    return data


def process_scenario(
    scenario: type[ConcreteScenario],
    *cls_path: tuple[type[MainModel], Path],
    exclude_checks: tuple[str] = (),
    display_formats: tuple[str] = (),
    html_report: bool = False,
    **kwargs,
):
    try:
        models_data = []
        for model_cls, file_path in cls_path:
            logger.info(
                f"↺ Loading '{model_cls.plural}' from '{file_path.name}'"
            )
            instances = load_model(model_cls, file_path)
            logger.info(
                f"✓ Loaded {len(instances)} '{model_cls.plural}' successfully"
            )
            models_data.append(instances)

        logger.info(f"↺ Preparing '{scenario.name}' scenario")
        scenario = scenario(*models_data, **kwargs)
        scenario.exclude_checks(exclude_checks)

        logger.info(f"→ Executing scenario with {len(scenario.checks)} checks")
        for check in scenario.checks:
            logger.info(f"◉ '{check.__name__}'")
            check_docs = check.__doc__.replace("\n", " ")
            logger.debug(f"\t{check_docs}")

        output = scenario.execute()
        results = scenario.analyze(output)
        scenario.show(results, display_formats)
        if html_report:
            logger.info("Saving analysis results as HTML report")
            html_code = export_as_html(
                scenario.analysis_results,
                scenario.execution_results,
                scenario.checks,
            )
            file_path = Path("report.html")
            file_path.write_text(html_code)
            logger.info(f"Report saved in {file_path.absolute()}")

    except Exception as ex:  # noqa: BLE001
        raise ClickException(f"{str(ex)}\n{ex.args}\n{ex.__cause__}")  # noqa: B904


if __name__ == "__main__":
    main()
