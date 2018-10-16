# -*- encoding: utf-8 -*-
"""
Config file to import fixtures with pytest
"""
import pytest

from sniwi.parser import LogParser


@pytest.fixture
def parser():
    """ Returns LogParser class"""
    return LogParser
