# -*- encoding: utf-8 -*-
"""
Test the parser class to ensure we collect the right amount of data
"""
import pytest
from datetime import datetime


class TestLogParser(object):
    """
    Test every method of LogParser
    with valid and invalid log string format
    """

    _log_sample = u"""64.242.88.10 \
                     - - \
                     [07/Mar/2004:16:05:49 -0800] \
                     "GET /twiki?topicparent=Main.Conf HTTP/1.1" \
                     401 \
                     12846 \
                    """
    _keys = ['agent',
             'cookies',
             'host',
             'referrer',
             'request',
             'size',
             'status',
             'time',
             'user']

    def test_valid_log_with_valid_string(self, parser):
        """
        Test if function works for valid input:

         - it get all the key we might need
         - it transform the date into a readable python format
         - it assert one value with accuracy.

         params:
            parser: Instance of LogParser (see conftest.py)
        """
        d = parser.valid_log(self._log_sample)

        assert all(key in d for key in self._keys)
        assert isinstance(d['time'], datetime)
        assert d['host'] == '64.242.88.10'

    # 'time': datetime.strptime('07/Mar/2004:16:05:49 -0800', )
    def test_valid_log_with_invalid_valid_string(self, parser):
        """
        Test if function returns empty dict for invalid input

         params:
            parser: Instance of LogParser (see conftest.py)
        """
        d = parser.valid_log(u'unvalidstring 漢字')

        assert d == {}
