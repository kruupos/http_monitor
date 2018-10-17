# -*- encoding: utf-8 -*-
"""
Sniffer, file reader class in "tail -f" mode
"""
import aiofiles
import asyncio
import os
import sys

from sniwi.parser import LogParser


class Sniffer(object):

    @classmethod
    async def readline_generator(cls, file):
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
        buffer = ''

        async with aiofiles.open(file, mode='r', encoding='utf-8', errors='ignore') as f:
            await f.seek(0, os.SEEK_END)

            while True:
                line = await f.readline()

                if not line:
                    await asyncio.sleep(1)
                    continue

                data = LogParser.std_log(line)

                if not data:
                    await asyncio.sleep(0.1)
                    if not buffer:
                        buffer = line
                    else:
                        buffer += line
                        data = LogParser.std_log(buffer)
                        buffer = ''

                yield data
