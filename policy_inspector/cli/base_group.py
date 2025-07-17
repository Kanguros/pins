import logging

try:
    import rich_click as click

    clickGroup = click.RichGroup
except ImportError:
    import click

    clickGroup = click.Group

logger = logging.getLogger(__name__)

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
    except FileNotFoundError:
        return
    except yaml.YAMLError as e:
        raise click.BadParameter(f"Invalid YAML in config file: {e}") from e

    ctx.default_map = {}

    for key, value in data.items():
        if key == "panorama" and isinstance(value, dict):
            for pano_key, pano_value in value.items():
                ctx.default_map[f"panorama_{pano_key}"] = pano_value
        elif isinstance(value, dict):
            ctx.default_map[key] = value
        else:
            if isinstance(value, list):
                value = tuple(value)
            ctx.default_map[key] = value

    logger.debug("Default map set from YAML: %s", ctx.default_map)
    logger.debug("Final ctx.default_map: %s", ctx.default_map)
    print("ctx.default_map:", ctx.default_map)


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

class VerboseGroup(clickGroup):
    """Click Group that automatically adds verbose option to all commands."""

    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        print(f"{self.__dict__.items()}")
        print(f"{self.params=}")
        self.params.append(verbose_option())
        self.params.append(config_option())

    def add_command(self, cmd, name=None):
        """Override to add verbose option to all commands."""
        print(f"{cmd.params=}")

        cmd.params.append(verbose_option())
        super().add_command(cmd, name)
