"""Command-line interface for Curriculum Repository System."""

import click
from curriculum import __version__
from curriculum.config import settings


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Curriculum Repository System CLI."""
    pass


@main.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(host: str, port: int, reload: bool) -> None:
    """Start the development server."""
    import uvicorn
    
    click.echo(f"Starting {settings.app_name} v{__version__}")
    click.echo(f"Environment: {settings.environment}")
    click.echo(f"Server: http://{host}:{port}")
    
    uvicorn.run(
        "curriculum.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower(),
    )


@main.command()
def check() -> None:
    """Check system configuration."""
    click.echo("Checking system configuration...")
    
    click.echo(f"✓ App Name: {settings.app_name}")
    click.echo(f"✓ Version: {__version__}")
    click.echo(f"✓ Environment: {settings.environment}")
    click.echo(f"✓ Debug: {settings.debug}")
    click.echo(f"✓ Database URL: {settings.database_url[:30]}...")
    click.echo(f"✓ Redis URL: {settings.redis_url}")
    
    if settings.enable_versioning:
        click.echo("✓ Versioning: Enabled")
    if settings.enable_analytics:
        click.echo("✓ Analytics: Enabled")
    
    click.echo("\n✓ Configuration check complete")


@main.command()
@click.option('--coverage', is_flag=True, help='Run with coverage')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def test(coverage: bool, verbose: bool) -> None:
    """Run the test suite."""
    import subprocess
    
    cmd = ["pytest"]
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    if verbose:
        cmd.append("-v")
    
    click.echo("Running tests...")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        click.echo("\n✓ All tests passed")
    else:
        click.echo("\n✗ Some tests failed", err=True)
    
    raise SystemExit(result.returncode)


@main.command()
def lint() -> None:
    """Run code quality checks."""
    import subprocess
    
    checks = [
        ("Black", ["black", "--check", "src/", "tests/"]),
        ("Flake8", ["flake8", "src/", "tests/"]),
        ("MyPy", ["mypy", "src/"]),
        ("isort", ["isort", "--check-only", "src/", "tests/"]),
    ]
    
    all_passed = True
    
    for name, cmd in checks:
        click.echo(f"\nRunning {name}...")
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            click.echo(f"✓ {name} passed")
        else:
            click.echo(f"✗ {name} failed", err=True)
            click.echo(result.stdout.decode())
            click.echo(result.stderr.decode())
            all_passed = False
    
    if all_passed:
        click.echo("\n✓ All checks passed")
    else:
        click.echo("\n✗ Some checks failed", err=True)
        raise SystemExit(1)


@main.command()
def format() -> None:
    """Format code with Black and isort."""
    import subprocess
    
    click.echo("Formatting code with Black...")
    subprocess.run(["black", "src/", "tests/"])
    
    click.echo("Sorting imports with isort...")
    subprocess.run(["isort", "src/", "tests/"])
    
    click.echo("✓ Code formatting complete")


@main.command()
@click.argument('name')
def create_service(name: str) -> None:
    """Create a new service template."""
    from pathlib import Path
    
    service_name = name.lower()
    class_name = ''.join(word.capitalize() for word in service_name.split('_'))
    
    service_content = f'''"""Service for {service_name}."""

from typing import Optional
from uuid import UUID


class {class_name}Service:
    """Service for managing {service_name}."""

    def __init__(self) -> None:
        """Initialize {service_name} service."""
        self._store: dict = {{}}

    def get(self, id: UUID) -> Optional[dict]:
        """Get item by ID."""
        return self._store.get(id)
'''
    
    service_path = Path(f"src/curriculum/services/{service_name}.py")
    service_path.write_text(service_content)
    
    click.echo(f"✓ Created service: {service_path}")
    click.echo(f"  Don't forget to:")
    click.echo(f"  1. Add to src/curriculum/services/__init__.py")
    click.echo(f"  2. Create tests in tests/test_{service_name}_service.py")


if __name__ == '__main__':
    main()
