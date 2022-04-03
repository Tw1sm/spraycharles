import pytest
from spraycharles import spraycharles as sc
from click.testing import CliRunner


def test_cli():

    runner = CliRunner()

    # No such option
    result = runner.invoke(sc.main, ["-x", "test"])
    assert "No such option" in result.output
