# -*- encoding: utf-8 -*-
"""
Test utils functions
"""
import pytest

from collections import defaultdict
from sniwi.utils import top_three, get_section


class TestUtils(object):
    """
    Test utils functions
    """
    @pytest.mark.parametrize('in_dict,out_list,explanation', [
        (
            {'max': 20, 'audrey': 50, 'sandra': 25, 'felix': 10},
            ['audrey    : 50', 'sandra    : 25', 'max       : 20'],
            'with normal dict'
        ),
        (
            defaultdict(int, {'max': 20, 'audrey': 50, 'sandra': 25, 'felix': 10}),
            ['audrey    : 50', 'sandra    : 25', 'max       : 20'],
            'with defaultdict'
        ),
        ({}, [], 'with empty dict'),
        ({'max': 20, 'audrey': 50}, ['audrey    : 50', 'max       : 20'], 'with small dict')
    ])
    def test_top_three(self, in_dict, out_list, explanation):
        """
        test top_three utils method

        params:
            in_dict: input dict or defaultdict to test
            out_list: return 'key: value' of top_three function
            explanation: (str), additionnal information for assert
        """
        assert top_three(in_dict) == out_list, explanation

    @pytest.mark.parametrize('url,section,explanation', [
        (
            'http://my.site.com/pages/ohers',
            '/pages',
            'with full url'
        ),
        (
            'http://my.site.com/pages?query',
            '/pages',
            'with defaultdict'
        ),
        (
            '/pages/others',
            '/pages',
            'without domain name'
        ),
        ('/', '/', 'minimalist'),
        ('NotanUrl', None, 'without an url')

    ])
    def test_get_section(self, url, section, explanation):
        """
        test get_section utils method

        params:
            ulr: (str) of an url
            section: (str) expected result
            explanation: (str), additionnal information for assert
        """
        assert get_section(url) == section, explanation
