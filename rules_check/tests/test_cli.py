


from click.testing import CliRunner
from rules_check.__main__ import main

def test_main_command():
  runner = CliRunner()
  result = runner.invoke(main, ['--help'])
  assert result.exit_code == 0
  assert 'Debug mode is on' in result.output
  assert 'Syncing' in result.output