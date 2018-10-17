# -*- encoding: utf-8 -*-
"""
Main entry of the program
"""

import sys

if sys.version_info < (3, 6):
    sys.exit('Sniwi requires Python 3.6+')

from sniwi.looper import main

sys.exit(main())
