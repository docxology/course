"""Tests for CLI module."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner


@pytest.mark.integration
class TestCLI:
    """Tests for CLI functionality."""

    def test_cli_import(self):
        """Test that CLI can be imported."""
        from curriculum.cli import main

        assert main is not None

    def test_cli_main_function(self):
        """Test that CLI main function exists."""
        from curriculum.cli import main

        assert callable(main)

    @patch("uvicorn.run")
    def test_cli_serve_command(self, run):
        from curriculum.cli import main

        result = CliRunner().invoke(main, ["serve", "--host", "127.0.0.1", "--port", "8123"])
        assert result.exit_code == 0, result.output
        run.assert_called_once()
        assert run.call_args.kwargs["host"] == "127.0.0.1"
        assert run.call_args.kwargs["port"] == 8123

    def test_cli_check_command(self):
        from curriculum.cli import main

        result = CliRunner().invoke(main, ["check"])
        assert result.exit_code == 0, result.output
        assert "Configuration check complete" in result.output

    @patch("subprocess.run")
    def test_cli_test_command(self, run):
        from curriculum.cli import main

        run.return_value.returncode = 0
        result = CliRunner().invoke(main, ["test", "--verbose", "--coverage"])
        assert result.exit_code == 0, result.output
        run.assert_called_once_with(
            ["pytest", "--cov=src", "--cov-report=html", "--cov-report=term", "-v"]
        )

    @patch("subprocess.run")
    def test_cli_lint_command(self, run):
        from curriculum.cli import main

        run.return_value.returncode = 0
        result = CliRunner().invoke(main, ["lint"])
        assert result.exit_code == 0, result.output
        assert [call.args[0][0] for call in run.call_args_list] == [
            "black",
            "flake8",
            "mypy",
            "isort",
        ]

    @patch("subprocess.run")
    def test_cli_format_command(self, run):
        from curriculum.cli import main

        result = CliRunner().invoke(main, ["format"])
        assert result.exit_code == 0, result.output
        assert [call.args[0][0] for call in run.call_args_list] == ["black", "isort"]

    def test_cli_create_service_command(self):
        from pathlib import Path

        from curriculum.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("src/curriculum").mkdir(parents=True)
            result = runner.invoke(main, ["create-service", "example"])
            assert result.exit_code == 0, result.output
            assert "class ExampleService" in Path("src/curriculum/example.py").read_text()

    def test_cli_version_option(self):
        from curriculum import __version__
        from curriculum.cli import main

        result = CliRunner().invoke(main, ["--version"])
        assert result.exit_code == 0, result.output
        assert __version__ in result.output

    def test_cli_group_decorator(self):
        """Test CLI group decorator."""
        from curriculum.cli import main

        # Verify it's decorated as a click group
        assert hasattr(main, "commands")

    def test_cli_commands_available(self):
        """Test that all CLI commands are available."""
        from curriculum.cli import main

        expected_commands = ["serve", "check", "test", "lint", "format", "create-service"]

        for command_name in expected_commands:
            assert command_name in main.commands, f"Command {command_name} not found"

    def test_cli_help_text(self):
        """Test CLI help text exists."""
        from curriculum.cli import main

        # The function should have docstring
        assert main.__doc__ is not None
        assert "Curriculum Repository System CLI" in main.__doc__

    def test_cli_serve_defaults(self):
        """Test CLI serve command default values."""
        from curriculum.cli import main

        serve_cmd = main.commands["serve"]

        # Check default parameter values
        assert serve_cmd.params[0].name == "host"  # First parameter should be host
        assert serve_cmd.params[1].name == "port"  # Second should be port

    def test_cli_test_coverage_option(self):
        """Test CLI test command coverage option."""
        from curriculum.cli import main

        test_cmd = main.commands["test"]

        # Should have coverage option
        coverage_param = next((p for p in test_cmd.params if p.name == "coverage"), None)
        assert coverage_param is not None

    def test_cli_test_verbose_option(self):
        """Test CLI test command verbose option."""
        from curriculum.cli import main

        test_cmd = main.commands["test"]

        # Should have verbose option
        verbose_param = next((p for p in test_cmd.params if p.name == "verbose"), None)
        assert verbose_param is not None
