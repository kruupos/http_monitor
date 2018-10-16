# -*- encoding: utf-8 -*-
"""
Main loop of the application
"""
import asyncio
from collections import defaultdict
from time import gmtime, strftime

# from sniwi.interface import ConsoleInterface
from sniwi.parser import LogParser
from sniwi.utils import timer, top_three
from sniwi.sniffer import Sniffer


HITS_PER_SECS_TRESHOLD = 20_000


class Sniwi(object):
    def __init__(self, loop, file_path=u'\\var\\log\\apache.log', alert_timer=120, stat_timer=10, alert_treshold=10):
        """
        Sniwi main class

        Instanciates - Sniffer (to watch from a file)
                     - Console Interface (the urwid interface)

        params:
            loop: asyncio main loop
            file_path: (str) the name of the file to watch
            alert_timer: (int) a timer to schedule the task alert
            stat_timer: (int) a timer to schedule the stat alert
            alert_treshold: (int) number of average requests to trigger an alert
        """
        self.file_path = file_path

        self.alert_timer = alert_timer
        self.stat_timer = stat_timer
        self.tick_timer = 1

        self.alert_treshold = alert_treshold

        self.tick_flag = asyncio.Event()

        self.alert_flag = False

        self.hit_per_sec = 0
        self.total_hit = 0
        self.hit_list = []

        self.url_section_dict = defaultdict(int)
        self.user_dict = defaultdict(int)

        # self.interface = ConsoleInterface(loop)
        self.sniffer = Sniffer(file_path)

    async def ui(self):
        """ start the console """
        pass
        # await self.interface.run()

    async def update_metrics(self, data):
        """ update main metrics of the application

        params:
            data: a dict of the parsed log file
        """

        # When there is too many data at once, the CPU cycle does not allowed
        # to run tick timer at the right time.
        if self.hit_per_sec > HITS_PER_SECS_TRESHOLD:
            await asyncio.sleep(0.1)

        if data['user']:
            self.user_dict[data['user']] += 1
        if data['section']:
            self.url_section_dict[data['section']] += 1
        self.hit_per_sec += 1
        self.total_hit += 1

    @timer('tick_timer')
    async def aio_readline(self):
        """
        read line from file_path and retrieve dict with various info
        at each lines
        """
        for data in self.sniffer.readline_generator():
            if not data:
                continue
            await self.update_metrics(data)

    @timer('tick_timer')
    async def tick(self):
        """ This task run every second as a clock to update the interface """
        self.tick_flag.set()
        self.hit_list.append(self.hit_per_sec)
        print(self.hit_per_sec)
        self.hit_per_sec = 0
        self.tick_flag.clear()

    @timer('alert_timer')
    async def alert(self):
        """ This task send alert to the interface """
        await self.tick_flag.wait()

        if self.hit_list:
            min_hits = min(self.hit_list)
            max_hits = max(self.hit_list)
            average_hits = sum(self.hit_list) / len(self.hit_list)
        self.hit_list.clear()

        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        if self.alert_flag and average_hits < self.alert_treshold:
            print(f'High traffic stopped at {time}')
            self.alert_flag = False
        elif average_hits >= self.alert_treshold:
            print(f'High traffic generated an alert - hits = {average_hits}, triggered at {time}')
            self.alert_flag = True

        print(average_hits)

    @timer('stat_timer')
    async def stat(self):
        """ This task give feedback from what happening every `stat_timer` to the interface """
        top_users = top_three(self.user_dict)
        self.user_dict.clear()

        top_sections = top_three(self.url_section_dict)
        self.url_section_dict.clear()

        print(top_sections)
        print(top_users)

    def shutdown_ui(self):
        """ This function is called in case of a SIGINT, it stops the interface properly """
        print('TOTAL HIT')
        print(self.total_hit)
        pass
        # self.interface.shutdown()
