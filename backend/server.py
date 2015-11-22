#!/usr/bin/env python

import asyncio
import websockets.server
import logging

import handler

async_logger = logging.getLogger("asyncio")
async_logger.setLevel(logging.WARNING)

han = handler.WebSocketHandler()

start_server = websockets.server.serve(han, 'localhost', 9007)

loop = asyncio.get_event_loop()
s = loop.run_until_complete(start_server)

print('serving...')
try:
    loop.run_forever()
except KeyboardInterrupt:
    print("exit.")
finally:
    loop.close()

