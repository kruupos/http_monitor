# -*- encoding: utf-8 -*-
"""
Config file to import fixtures with pytest
"""
import pytest

from sniwi.parser import LogParser
from sniwi.sniwi import Sniwi


@pytest.fixture
def parser():
    """ Returns LogParser class"""
    return LogParser
