# -*- encoding: utf-8 -*-
"""
Sniffer, file reader class in "tail -f" mode
"""
import aiofiles
import asyncio
import os

from sniwi.parser import LogParser


class Sniffer(object):

    def __init__(self, file_path):
        """
        First open file in read mode,
        If the file exists and is readable, go to EOF
        """
        self.file_path = file_path

    async def readline_generator(self):
        """
        Read every new line appening in the file and yield it

        Then use LogParser to retrieve needed info in a dict

        if LogParse fail, this doesnt necessarally mean log is corrupted
        but we may reaching EOF before newline, that why we can retry a second time

        if data is truly corrupted, the generator returns None

       is intended to be used as a generator:
        example:
            async for line in sniffer.readline_generator():
                # do stuff with line
        """
        # Needed to handle half line when reaching EOF before a newline
        self.buffer = ''

        async with aiofiles.open(self.file_path, mode='r', encoding='utf-8', errors='ignore') as f:
            await f.seek(0, os.SEEK_END)

            while True:
                line = await f.readline()

                if not line:
                    await asyncio.sleep(1)
                    continue

                data = LogParser.std_log(line)

                if not data:
                    if not self.buffer:
                        self.buffer = line
                    else:
                        self.buffer += line
                        data = LogParser.std_log(self.buffer)
                        self.buffer = ''

                yield data
