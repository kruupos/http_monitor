# -*- encoding: utf-8 -*-
"""
Decrepyt information of log files and retrieve needed information
"""
import re
from datetime import datetime


class LogParser(object):
    """
    LogParser

    parse every line of log following NCSA Common log format
    and retrieves needed information

    References:
        https://en.wikipedia.org/wiki/Common_Log_Format
        https://github.com/michael-lazar/Akita/blob/master/akita/parser.py
    """

    # Regex for the common Apache log format.
    __valid_log_parts = [
        r'(?P<host>\S+)',              # host %h
        r'\s+\S+',                     # indent %l (unused)
        r'\s+(?P<user>\S+)',           # user %u
        r'\s+\[(?P<time>.+)\]',        # time %t
        r'\s+"(?P<request>.*)"',       # request "%r"
        r'\s+(?P<status>[0-9]+)',      # status %>s
        r'\s+(?P<size>\S+)',           # size %b (careful, can be '-')
        r'(\s+"(?P<referrer>.*?)")?',  # referrer "%{Referer}i"
        r'(\s+"(?P<agent>.*?)")?',     # user agent "%{User-agent}i"
        r'(\s+"(?P<cookies>.*?)")?',   # cookies "%{Cookies}i"
    ]

    __date_fmt = '%d/%b/%Y:%H:%M:%S %z'

    __pattern = re.compile(r''.join(__valid_log_parts)+r'\s*\Z')

    @classmethod
    def valid_log(cls, log):
        """
        params:
            log: str

        Parse log line using regexp defined in instance variable __parts

        As regular expression can return an perfectly usable dictionnary
        there is no need to create instance variables

        returns dict if valid
        example: {
                'host':     '72.129.137.65',
                'user':     '-'
                'time':     datetime('27/Mar/2018:10:15:27 -0400'),
                'request':  'GET /item/electronics/4380 HTTP/1.1',
                'status':   '200',
                'size':     '43',
                'referrer': '/category/books',
                'agent':    'Mozilla/5.0 (Windows NT 6.1; WOW64)',
                'cookies':  None
            }

        Note that data not found will be equal to None (see cookies).

        else return empty dict.
        """
        _match = cls.__pattern.match(log)

        if not _match:
            return {}

        d = _match.groupdict()

        if d['time']:
            d['time'] = datetime.strptime(d['time'], cls.__date_fmt)

        return d

        # TODO
        # Create another classmethod for invalid log
        # located in /var/log/apache/error.log
