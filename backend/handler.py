#! /usr/bin/env python

import asyncio
import websockets
import uuid
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketHandler:
    def __init__(self):
        self.users = {}

    async def _send(self, ws, mes):
        try:
            await ws.send(mes.encode())
        except websockets.exceptions.InvalidState:
            logger.warning("EInvalidState")
            return "EInvalidState"

    async def __call__(self, ws, uri):
        name = await ws.recv()
        iden = uuid.uuid4().hex
        message = json.dumps({'iden': iden})
        await self._send(ws, message)
        self.users.update({name: {'iden':iden, 'ws':ws}})
        logger.info("{} connected".format(name))
        await self.update_list()
        await self.run(name)

    async def run(self, name):
        ws = self.users[name]['ws']
        iden = self.users[name]['iden']
        while ws.open:
            data = await ws.recv()
            if data is None or data == "pong":
                continue
            data = data.decode()
            data = json.loads(data)
            if data['iden'] != iden:
                await self._send(ws, "EWrongIden")
                break
            try:
                to, mes = data['to'], data['message']
            except KeyError:
                await self._send(ws, json.dumps({"error":"EFormat"}))
                continue

            logger.info(" {} > {} : {}".format(name, to, mes))
            res = await self.route_message(name, to, mes)
            if res:
                await self._send(ws, json.dumps({"error", res}))
            else:
                await self._send(ws, json.dumps({"result":"successed"}))
        try:
            del self.users[name]
            logger.info("{} disconnected".format(name))
        except KeyError:
            logger.warning("{} not found in users".format(name))
        finally:
            await self.update_list()

    async def route_message(self, fr, to, message):
        ws = self.users[to]['ws']
        if not ws.open:
            return "EUserOffline"
        else:
            send_data = {'from': fr, 'message': message}
            await self._send(ws, json.dumps(send_data))

    async def update_list(self):
        user_list = list(self.users.keys())
        for user in self.users.values():
            ws = user['ws']
            await self._send(ws, json.dumps({'user_list':user_list}))


