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

    @asyncio.coroutine
    def _send(self, ws, mes):
        try:
            yield from ws.send(mes.encode())
        except websockets.exceptions.InvalidState:
            logger.warning("EInvalidState")
            return "EInvalidState"

    @asyncio.coroutine
    def __call__(self, ws, uri):
        name = yield from ws.recv()
        iden = uuid.uuid4().hex
        message = json.dumps({'iden': iden})
        yield from self._send(ws, message)
        self.users.update({name: {'iden':iden, 'ws':ws}})
        logger.info("{} connected".format(name))
        yield from self.update_list()
        yield from self.run(name)

    @asyncio.coroutine
    def run(self, name):
        ws = self.users[name]['ws']
        iden = self.users[name]['iden']
        while ws.open:
            data = yield from ws.recv()
            if data is None or data == "pong":
                continue
            data = data.decode()
            data = json.loads(data)
            if data['iden'] != iden:
                yield from self._send(ws, "EWrongIden")
                break
            try:
                to, mes = data['to'], data['message']
            except KeyError:
                yield from self._send(ws, json.dumps({"error":"EFormat"}))
                continue

            logger.info(" {} > {} : {}".format(name, to, mes))
            res = yield from self.route_message(name, to, mes)
            if res:
                yield from self._send(ws, json.dumps({"error", res}))
            else:
                yield from self._send(ws, json.dumps({"result":"successed"}))
        try:
            del self.users[name]
            logger.info("{} disconnected".format(name))
        except KeyError:
            logger.warning("{} not found in users".format(name))
        finally:
            yield from self.update_list()

    @asyncio.coroutine
    def route_message(self, fr, to, message):
        ws = self.users[to]['ws']
        if not ws.open:
            return "EUserOffline"
        else:
            send_data = {'from': fr, 'message': message}
            yield from self._send(ws, json.dumps(send_data))

    @asyncio.coroutine
    def update_list(self):
        user_list = list(self.users.keys())
        for user in self.users.values():
            ws = user['ws']
            yield from self._send(ws, json.dumps({'user_list':user_list}))


