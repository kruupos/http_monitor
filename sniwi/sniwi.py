# -*- encoding: utf-8 -*-
"""
Main loop of the application
"""
import asyncio
from collections import defaultdict, deque

from sniwi.interface import ConsoleInterface
from sniwi.parser import LogParser
from sniwi.utils import top_three
from sniwi.sniffer import Sniffer


class Sniwi(object):
    def __init__(self, loop, file_path, threshold_max_hits=10, alert_interval=120, traffic_interval=10):
        """
        Sniwi main class

        Instanciates - Sniffer (to watch from a file)
                     - Console Interface (the urwid interface)

        params:
            loop: asyncio main loop
            file_path: (str) the name of the file to watch
            threshold_max_hits: (int) number of average requests to trigger an alert
            alert_interval: (int) interval in second for alert
            traffic_interval: (int) interval in second for refreshing traffic information
        """
        self.file_path = file_path

        self.threshold_max_hits = threshold_max_hits

        self.alert_flag = False

        self.hit_per_sec = 0
        self.total_hit = 0
        self.alert_deque = deque(maxlen=alert_interval)
        self.traffic_deque = deque(maxlen=traffic_interval)

        self.url_section_dict = defaultdict(int)
        self.user_dict = defaultdict(int)

        self.interface = ConsoleInterface(loop, file_path, threshold_max_hits, alert_interval, traffic_interval)
        self.sniffer = Sniffer(file_path)

    async def ui(self):
        """ start the console """
        await self.interface.run()

    async def update_metrics(self, data):
        """ update main metrics of the application

        params:
            data: a dict of the parsed log file
        """
        if data['user']:
            self.user_dict[data['user']] += 1
        if data['section']:
            self.url_section_dict[data['section']] += 1
        self.hit_per_sec += 1
        self.total_hit += 1

    async def aio_readline(self):
        """
        read line from file_path and retrieve dict with various info
        at each lines
        """
        async for data in self.sniffer.readline_generator():
            if not data:
                continue
            await self.update_metrics(data)

    async def tick(self):
        """ This task run every second as a clock to update the interface """
        self.alert_deque.append(self.hit_per_sec)
        self.traffic_deque.append(self.hit_per_sec)
        self.interface.update_hits(self.hit_per_sec, self.total_hit)
        self.hit_per_sec = 0

    async def alert(self):
        """ This task send alert to the interface """
        average_hits = sum(self.alert_deque) / len(self.alert_deque) if self.alert_deque else 0

        if self.alert_flag and average_hits < self.threshold_max_hits:
            self.alert_flag = False
            self.interface.update_alert(self.alert_flag, average_hits)
        elif not self.alert_flag and average_hits >= self.threshold_max_hits:
            self.alert_flag = True
            self.interface.update_alert(self.alert_flag, average_hits)

    async def traffic(self):
        """ This task give feedback from what happening every `traffic_interval` to the interface """
        top_users = top_three(self.user_dict)
        self.user_dict.clear()

        top_sections = top_three(self.url_section_dict)
        self.url_section_dict.clear()

        self.interface.update_traffic(top_sections, top_users, self.traffic_deque)

    def shutdown_ui(self):
        """ This function is called in case of a SIGINT, it stops the interface properly """
        self.interface.shutdown()
