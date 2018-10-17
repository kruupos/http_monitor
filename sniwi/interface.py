# -*- encoding: utf-8 -*-
"""
Display console interface monitor with urwid
"""

import urwid
import asyncio
from time import gmtime, strftime

from collections import deque


class ConsoleInterface(object):
    """ class intended to create the frame
        and different option
    """
    def __init__(self, loop, file_path, threshold_max_hits, alert_interval, traffic_interval):
        """
        Init every frame needed for the display, the method mostly change the content of the text
        """
        self.flag = asyncio.Event()

        self.file_path = file_path
        self.threshold_max_hits = threshold_max_hits
        self.alert_interval = alert_interval
        self.traffic_interval = traffic_interval

        # Set up color scheme
        palette = [
            ('background', 'white,bold', 'dark cyan'),
            ('subpart', 'yellow,bold', 'dark cyan'),
            ('number', 'yellow,bold', 'dark cyan'),
            ('titlebar', 'black', 'dark blue'),
            ('quit button', 'white', 'dark blue'),
            ('alert', 'light gray,standout', 'dark red'),
            ('success', 'black,standout', 'dark green')]

        # Left
        self.trafic_title = f'Traffic info section -- refreshing rate: {self.traffic_interval}/sec'

        self.list_sections = urwid.SimpleFocusListWalker([])
        self.list_box_sections = urwid.ListBox(self.list_sections)
        self.list_box_sections = urwid.Padding(self.list_box_sections, width=('relative', 50))
        self.left_panel = urwid.Frame(self.list_box_sections, urwid.Text(('subpart', 'Top three sections\n')))
        self.left_panel = urwid.LineBox(self.left_panel, self.trafic_title, bline='', tline='-')

        self.list_users = urwid.SimpleFocusListWalker([])
        self.list_box_users = urwid.ListBox(self.list_users)

        self.middle_panel = urwid.Frame(self.list_box_users, urwid.Text(('subpart', 'Top three users\n')))
        self.middle_panel = urwid.LineBox(self.middle_panel, bline='', tline='')

        self.total_hits = urwid.Text([u'Total Hits: ', ('number', '0')])
        self.hits_per_sec = urwid.Text([u'Hit/sec   : ', ('number', '0'), '\n\n'])
        self.average = urwid.Text(f'average hits per {self.traffic_interval}/sec: 0')
        self.min_hit = urwid.Text(f'min hit      per {self.traffic_interval}/sec: 0')
        self.max_hit = urwid.Text(f'max hit      per {self.traffic_interval}/sec: 0')

        threshold_text = f'alert threshold > {threshold_max_hits} requests per sec in average over {self.alert_interval} seconds\n'
        self.threshold_max_hits = urwid.Text(threshold_text)
        self.file_path = urwid.Text([u'currently sniffing on:', ('alert', f'{file_path}'), '\n'])

        list_down_panel = [self.total_hits, self.hits_per_sec, self.average, self.min_hit, self.max_hit]
        self.down_panel = urwid.LineBox(urwid.Pile(list_down_panel), title='Traffic', tline='.')

        list_top_panel = [self.threshold_max_hits, self.file_path]
        self.top_panel = urwid.LineBox(urwid.Pile(list_top_panel), title='General Information', bline='', tline='=')

        self.left_panel = urwid.Pile([
            ('pack', self.top_panel), self.left_panel, self.middle_panel, ('pack', self.down_panel)
        ])

        # Right
        self.alert_title = f'Alert logging -- refreshing rate {self.alert_interval}/sec'

        self.list_alerts = urwid.SimpleFocusListWalker([])
        self.list_box_alerts = urwid.ListBox(self.list_alerts)
        list_box_padding = urwid.Padding(self.list_box_alerts, width=('relative', 95), align='center')
        self.header_alert = urwid.Text(('subpart', 'Alert list\n'))
        self.right_panel = urwid.Frame(list_box_padding, self.header_alert)
        self.right_panel = urwid.LineBox(self.right_panel, title=self.alert_title, lline='')

        # Columns
        columns = urwid.Columns([self.left_panel, self.right_panel], focus_column=1)
        fill = urwid.Filler(columns, 'top')

        # Main Frame
        header_text = urwid.Text(u'Sniwi: Sniffer Kiwi HTTP log monitoring')
        header = urwid.AttrMap(header_text, 'titlebar')

        footer_text = urwid.Text([u'Press (', ('quit button', u'Q'), u') to quit.'])
        footer = urwid.AttrMap(footer_text, 'titlebar')

        self.frame = urwid.Frame(columns, header, footer)
        self.frame = urwid.AttrMap(self.frame, 'background')

        # Create the event loop
        self.main_loop = urwid.MainLoop(
                self.frame,
                palette,
                event_loop=urwid.AsyncioEventLoop(loop=loop),
                unhandled_input=self.handle_input,
        )

    def update_hits(self, hits_per_sec, total_hits):
        self.total_hits.set_text([u'Total Hits: ', ('number', f'{total_hits}')])
        self.hits_per_sec.set_text([u'Hit/sec   : ', ('number', f'{hits_per_sec}'), '\n\n'])

    def update_traffic(self, top_sections, top_users, hit_list):
        self.list_sections.clear()
        for section in top_sections:
            self.list_sections.append(urwid.Text(section))

        self.list_users.clear()
        for user in top_users:
            self.list_users.append(urwid.Text(user))

        if hit_list:
            self.min_hit.set_text(f'min hit      per {self.traffic_interval}/sec: {min(hit_list)}')
            self.max_hit.set_text(f'max hit      per {self.traffic_interval}/sec: {max(hit_list)}')
            avg = sum(hit_list) / len(hit_list)
            self.average.set_text(f'average hits per {self.traffic_interval}/sec: {int(avg)}')
        else:
            self.min_hit.set_text(f'min hit      per {self.traffic_interval}/sec: 0')
            self.max_hit.set_text(f'max hit      per {self.traffic_interval}/sec: 0')
            self.average.set_text(f'average hits per {self.traffic_interval}/sec: 0')

    def update_alert(self, alert_flag, average_hits):
        t = strftime("%H:%M:%S, %a, %d %b %Y", gmtime())

        if alert_flag:
            alert_msg = urwid.Text([('alert', f'High traffic generated an alert - hits = {int(average_hits)}, triggered at {t}')])
        else:
            alert_msg = urwid.Text([('success', f'High traffic came back to normal at {t}')])

        self.list_alerts.append(alert_msg)

    # Handle key presses
    def handle_input(self, key):
        if key in ('Q', 'q'):
            self.flag.set()
            self.main_loop.stop()

    def shutdown(self):
        self.main_loop.stop()
        self.flag.set()

    async def run(self):
        self.main_loop.start()
        self.main_loop.draw_screen()
        await self.flag.wait()
