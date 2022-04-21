import pytest
from click.testing import CliRunner

from spraycharles import spraycharles as sc


def test_cli():

    runner = CliRunner()

    # No such option
    result = runner.invoke(sc.main, ["-x", "test"])
    assert "No such option" in result.output
