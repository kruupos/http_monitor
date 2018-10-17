# -*- encoding: utf-8 -*-
"""
Test tasks defined in Sniwi class
"""
import asyncio
import pytest
from collections import defaultdict

from sniwi.sniwi import Sniwi


class TestSniwi(object):
    """
    Test methods of Sniwi class
    """

    @pytest.mark.asyncio
    async def test_tick(self, event_loop):
        """
        tick should send hit_per_second info to interface and reset self.hit_per_sec
        """
        sniwi = Sniwi(event_loop, '')

        # let's predend there is a hit
        sniwi.hit_per_sec += 1

        await sniwi.tick()

        assert sniwi.hit_per_sec == 0

    @pytest.mark.asyncio
    async def test_stat(self, event_loop):
        """
        stat should send top three users and top three sections to the interface
        and clear the dicts
        """
        sniwi = Sniwi(event_loop, '')

        # let's predend there is top_users
        sniwi.users_dict = defaultdict(int, {'max': 20, 'audrey': 50, 'sandra': 25, 'felix': 10})

        await sniwi.stat()

        assert sniwi.user_dict == defaultdict(int)

    @pytest.mark.asyncio
    async def test_alert(self, event_loop):
        """
        alert should send an alert (flag set to True) when average thresold hit per seconds is reached
        and send another alert (flag set to False) when average thresold hit per seconds is not reached
        """
        sniwi = Sniwi(event_loop, '')

        # let's pretend the hit list reach 50 hits per seconds for 2 minutes
        sniwi.hit_list = [50] * 120

        assert sniwi.alert_flag is False

        # first call to alert
        await sniwi.alert()

        assert sniwi.alert_flag is True
        assert sniwi.hit_list == []

        # second call to alert
        await sniwi.alert()

        assert sniwi.alert_flag is False
