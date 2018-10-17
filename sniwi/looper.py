# -*- encoding: utf-8 -*-
"""
Main loop of the application
"""
from contextlib import suppress
import asyncio
import functools
import argparse
import sys
import os

from sniwi.sniwi import Sniwi


def get_args():
    parser = argparse.ArgumentParser(prog='sniwi')
    parser.add_argument(
        '-f', '--file-path',
        default=u'/var/log/apache.log',
        metavar='PATH',
        type=str,
        help='path of monitoring file')

    parser.add_argument(
        '-i', '--threshold-max-hits',
        metavar='SECOND',
        default=10,
        type=int,
        help='ratio requests/secs to trigger an alert')

    parser.add_argument(
        '-a', '--alert-interval',
        metavar='SECOND',
        default=120,
        type=int,
        help='Interval for alert')

    parser.add_argument(
        '-t', '--traffic-interval',
        metavar='SECOND',
        default=10,
        type=int,
        help='Interval for refreshing traffic information')
    return parser.parse_args()


def cancel_task(task, loop):
    """
    Ensure all tasks are cancel when the loop is completed or interrupted
    """
    task.cancel()
    with suppress(asyncio.CancelledError):
        loop.run_until_complete(task)


def schedule(f, interval):
    """
    Decorator template for method's class,
    will run itself every `interval` seconds.
    Is asynchronous

    params:
        timer: (int) interval in second
    """
    from functools import wraps

    @wraps(f)
    async def wrapper(*args, **kwargs):
        while True:
            await asyncio.sleep(interval)
            await f(*args, **kwargs)
    return asyncio.ensure_future(wrapper())


def main():
    """
    main loop of the application

    it create 5 tasks that runs undependently (but with lock):
        - `ui_task`: starts the ui to display alerts and other info
        - `tick_task`: collect number of hits per second
        - `sniffer_task`: reads in async mode the EOF of '/var/log/apache.log'
          (or other given files)
        - `alert_task`: schedule a timer to launch an alert (if needed)
           every X time
        - `traffic_task`: schedule a timer to display information of the taffic
           every X time

    All the tasks are defined in the main class Sniwi()
    It loops till the UI is up,
    that means the UI must implement his own shutdown mechanism.

    If an SIGINT (ctrl+c) is send to the app,
    then KeyboardInterrupt is triggered
    in other term the application stop.
    """
    args = get_args()

    if not os.path.isfile(args.file_path):
        sys.stderr.write('your path file is invalid\n')
        return -1

    loop = asyncio.get_event_loop()
    proc = Sniwi(loop=loop,
                 file_path=args.file_path,
                 threshold_max_hits=args.threshold_max_hits,
                 alert_interval=args.alert_interval,
                 traffic_interval=args.traffic_interval)

    ui_task = asyncio.ensure_future(proc.ui())
    sniffer_task = asyncio.ensure_future(proc.aio_readline())

    tick_task = schedule(proc.tick, interval=1)
    alert_task = schedule(proc.alert, interval=args.alert_interval)
    traffic_task = schedule(proc.traffic, interval=args.traffic_interval)
    try:
        loop.run_until_complete(ui_task)
    except KeyboardInterrupt:
        proc.shutdown_ui()
    finally:
        for task in [sniffer_task, tick_task, alert_task, traffic_task]:
            cancel_task(task, loop)
        loop.close()

        # # After the changes in 3.7
        # asyncio.gather(*asyncio.all_tasks()).cancel()
