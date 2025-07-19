import click
from typing import Callable, Iterable, Optional

def verbose_callback(ctx: click.Context, param, value) -> None:
    """Callback function for verbose option."""
    if not value:
        return
    _logger = logging.getLogger(__name__).parent
    count = len(value)
    if count > 0:
        _logger.setLevel(logging.DEBUG)
    if count > 1:
        handler = _logger.handlers[0]
        handler._log_render.show_level = True
    if count > 2:
        handler = _logger.handlers[0]
        handler._log_render.show_path = True
        handler._log_render.show_time = True


def verbose_option() -> click.Option:
    return click.Option(
        ["-v", "--verbose"],
        is_flag=True,
        multiple=True,
        callback=verbose_callback,
        expose_value=False,
        is_eager=True,
        help="More verbose and detailed output with each `-v` up to `-vvvv`",
    )

def configure_from_yaml(ctx, param, filename):
    """
    Callback for --config option that reads YAML configuration file
    and sets ctx.default_map for Click to use as parameter defaults.

    Args:
        ctx: Click context
        param: The parameter object (not used)
        filename: Path to the YAML configuration file
    """
    if filename is None:
        return
    import yaml
    try:
        with open(filename) as f:
            data = yaml.safe_load(f) or {}
        ctx.default_map = data
        logger.debug("Default map set from YAML: %s", ctx.default_map)
    except FileNotFoundError:
        return
    except yaml.YAMLError as e:
        raise click.BadParameter(f"Invalid YAML in config file: {e}") from e

    v = "\n".join([f"{k}={v}" for k, v in ctx.__dict__.items()])
    print(f"CONFIG OPTION CALLBACK:\n{v}")

def config_option(
    config_file_name: str = "--config", default: str = "config.yaml"
):
    """
    Decorator that adds a --config option to read defaults from a YAML file.

    This uses Click's ctx.default_map mechanism to set parameter defaults
    from the configuration file. The configuration file is processed eagerly
    before other options.

    Args:
        config_file_name: The option name (default: "--config")
        default: Default config file name
        help_text: Help text for the option

    Returns:
    """

    return click.Option(
            [config_file_name],
            type=click.Path(dir_okay=False),
            default=default,
            callback=configure_from_yaml,
            is_eager=True,
            expose_value=False,
            help="Read configuration from YAML file",
            show_default=True,
        )

def export_options(
    command: Callable, export_formats: Iterable[str] = ()
) -> Callable:
    """
    Decorator to add export format and export directory options to a Click command.

    Args:
        command: The Click command function.
        scenario_info: Optional scenario information dict.

    Returns:
        The decorated command function.
    """
    command = click.option(
        "--export",
        multiple=True,
        type=click.Choice(export_formats),
        help="Export formats (can be specified multiple times)",
    )(command)
    
    return click.option(
        "--export-dir", default=".", help="Directory to save exported files"
    )(command)


def display_option(
    command: Callable, display_formats: Iterable[str] = ()
) -> Callable:
    """
    Decorator to add display format option to a Click command.

    Args:
        command: The Click command function.
        scenario_info: Optional scenario information dict.

    Returns:
        The decorated command function.
    """
    return click.option(
        "-d",
        "--display",
        multiple=True,
        type=click.Choice(display_formats),
        default=["text"],
        help="Display formats (can be specified multiple times)",
    )(command)


def panorama_options(command: click.Command) -> click.Command:
    """
    Add Panorama connection options to a command.

    Args:
        command: Click command to modify

    Returns:
        Modified command with Panorama options
    """
    options = [
        click.option(
            "--panorama-hostname",
            help="Panorama hostname or IP address",
        ),
        click.option("--panorama-username", help="Panorama username"),
        click.option(
            "--panorama-password",
            help="Panorama password",
        ),
        click.option(
            "--panorama-api-version",
            default="v11_.1",
            show_default=True,
            help="Panorama API version",
        ),
        click.option(
            "--panorama-verify-ssl",
            default=False,
            help="Verify SSL certificates",
        ),
    ]
    for option in reversed(options):
        command = option(command)
    return command
