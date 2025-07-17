import logging

try:
    import rich_click as click
    clickGroup = click.RichGroup
except ImportError:
    import click
    clickGroup = click.Group

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


class VerboseGroup(clickGroup):
    """Click Group that automatically adds verbose option to all commands."""

    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        self.params.append(verbose_option())

    def add_command(self, cmd, name=None):
        """Override to add verbose option to all commands."""
        cmd.params.append(verbose_option())
        super().add_command(cmd, name)

