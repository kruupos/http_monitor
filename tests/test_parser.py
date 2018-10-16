# -*- encoding: utf-8 -*-
"""
Test the parser class to ensure we collect the right amount of data
"""
import pytest
from datetime import datetime
import json


def load_json_list(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return [tuple(l) for l in data['data']]


class TestLogParser(object):
    """
    Test every method of LogParser
    with valid and invalid log string format
    """

    _keys = ['agent',
             'cookies',
             'host',
             'referrer',
             'request',
             'method',
             'url',
             'section',
             'size',
             'status',
             'time',
             'user']

    @pytest.mark.parametrize('line,user,section,explanation', load_json_list('tests/test_log.json'))
    def test_std_log_with_valid_string(self, parser, line, user, section, explanation):
        """
        Test if function works for valid input:

         - it get all the key we might need
         - it transform the date into a readable python format
         - it assert one value with accuracy.

         params:
            parser: LogParser class (see conftest.py)
        """
        d = parser.std_log(line)
        assert all(key in d for key in self._keys), explanation
        assert isinstance(d['time'], datetime), explanation
        assert d['user'] == user, explanation
        assert d['section'] == section, explanation

    def test_valid_log_with_invalid_valid_string(self, parser):
        """
        Test if function returns empty dict for invalid input

         params:
            parser: LogParser class (see conftest.py)
        """
        d = parser.std_log(u'unvalidstring 漢字')

        assert d is None
