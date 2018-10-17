# -*- encoding: utf-8 -*-
"""
Test tasks defined in Sniwi class
"""
import asyncio
import pytest
from collections import defaultdict, deque
from pytest_mock import mocker
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
    async def test_traffic(self, event_loop):
        """
        traffic should send top three users and top three sections to the interface
        and clear the dicts
        """
        sniwi = Sniwi(event_loop, '')

        # let's predend there is top_users
        sniwi.users_dict = defaultdict(int, {'max': 20, 'audrey': 50, 'sandra': 25, 'felix': 10})

        await sniwi.traffic()

        assert sniwi.user_dict == defaultdict(int)

    @pytest.mark.asyncio
    async def test_alert(self, event_loop, mocker):
        """
        alert should send an alert (flag set to True) when average threshold hit per seconds is reached
        and send another alert (flag set to False) when average threshold hit per seconds is not reached

        it should not send an alert twice if it already sended one.

        To send an alert, it call ConsoleInterface instance interface `update_alert` method.
        """
        sniwi = Sniwi(event_loop, '')

        # let's pretend 50 requests have been made per second for 2 minutes
        sniwi.alert_deque = deque([50] * 120)

        # let's mock update_alert
        mocker.patch.object(sniwi.interface, 'update_alert')
        sniwi.interface.update_alert.return_value = None

        assert sniwi.alert_flag is False

        # first call to alert
        await sniwi.alert()

        assert sniwi.alert_flag is True
        sniwi.interface.update_alert.assert_called_with(True, 50)

        # second call to alert
        await sniwi.alert()

        assert sniwi.alert_flag is True
        # ensure update_alert have not been called again
        sniwi.interface.update_alert.assert_called_once()

        # now let's pretend 0 requests have been made per second for 2 minutes
        sniwi.alert_deque = deque([0] * 120)

        # third call to alert
        await sniwi.alert()

        assert sniwi.alert_flag is False
        sniwi.interface.update_alert.assert_called_with(False, 0)
