# -*- encoding: utf-8 -*-
"""
Main loop of the application
"""
from contextlib import suppress
import asyncio

from sniwi.sniwi import Sniwi


def cancel_task(task, loop):
    """
    Ensure all tasks are cancel when the loop is completed or interrupted
    """
    task.cancel()
    with suppress(asyncio.CancelledError):
        loop.run_until_complete(task)


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
        - `stat_task`: schedule a timer to display information of the taffic
           every X time

    All the tasks are defined in the main class Sniwi()
    It loops till the UI is up,
    that means the UI must implement his own shutdown mechanism.

    If an SIGINT (ctrl+c) is send to the app,
    then KeyboardInterrupt is triggered
    in other term the application stop.
    """
    print('start program')
    loop = asyncio.get_event_loop()
    proc = Sniwi(loop, 'file.log')

    # Starts the ui to display alerts and other info
    ui_task = asyncio.ensure_future(proc.ui())

    # Reads in async mode the EOF of '/var/log/apache.log'
    sniffer_task = asyncio.ensure_future(proc.aio_readline())

    # Collect number of hits per seconds
    tick_task = asyncio.ensure_future(proc.tick())

    # Schedule a timer to launch an alert every X time
    alert_task = asyncio.ensure_future(proc.alert())

    # schedule a timer to display information of the taffic
    stat_task = asyncio.ensure_future(proc.stat())
    try:
        loop.run_forever()
        # loop.run_until_complete(ui_task)
    except KeyboardInterrupt:
        proc.shutdown_ui()
    finally:
        for task in [sniffer_task, tick_task, alert_task, stat_task]:
            cancel_task(task, loop)
        loop.close()
        print('ending program')
