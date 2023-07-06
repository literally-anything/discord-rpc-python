import asyncio
import inspect
import json
import os
import struct
import sys
import tempfile
from typing import Union, Optional

# TODO: Get rid of this import * lol
from .exceptions import *
from .payloads import Payload
from .utils import get_ipc_path, get_event_loop


class BaseClient:

    def __init__(self,
                 client_id: str,
                 loop: asyncio.AbstractEventLoop = None,
                 **kwargs):
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self.pipe = kwargs.get('pipe', None)
        self.isasync = kwargs.get('isasync', False)
        self.connection_timeout = kwargs.get('connection_timeout', 30)
        self.response_timeout = kwargs.get('response_timeout', 10)

        client_id = str(client_id)

        self.sock_reader: Optional[asyncio.StreamReader] = None
        self.sock_writer: Optional[asyncio.StreamWriter] = None

        self.client_id = client_id

        if getattr(self, "on_event", None):  # Tasty bad code ;^)
            self._events_on = True
        else:
            self._events_on = False

    async def read_output(self):
        try:
            preamble = await asyncio.wait_for(self.sock_reader.read(8), self.response_timeout)
            status_code, length = struct.unpack('<II', preamble[:8])
            data = await asyncio.wait_for(self.sock_reader.read(length), self.response_timeout)
        except (BrokenPipeError, struct.error):
            raise PipeClosed
        except asyncio.TimeoutError:
            raise ResponseTimeout
        payload = json.loads(data.decode('utf-8'))
        if payload["evt"] == "ERROR":
            raise ServerError(payload["data"]["message"])
        return payload

    def send_data(self, op: int, payload: Union[dict, Payload]):
        if isinstance(payload, Payload):
            payload = payload.data
        payload = json.dumps(payload)

        assert self.sock_writer is not None, "You must connect your client before sending events!"

        self.sock_writer.write(
                struct.pack(
                        '<II',
                        op,
                        len(payload)) +
                payload.encode('utf-8'))

    async def handshake(self):
        ipc_path = get_ipc_path(self.pipe)
        if not ipc_path:
            raise DiscordNotFound

        try:
            if sys.platform == 'linux' or sys.platform == 'darwin':
                self.sock_reader, self.sock_writer = await asyncio.wait_for(asyncio.open_unix_connection(ipc_path), self.connection_timeout)
            elif sys.platform == 'win32' or sys.platform == 'win64':
                self.sock_reader = asyncio.StreamReader(loop=self._loop)
                reader_protocol = asyncio.StreamReaderProtocol(self.sock_reader, loop=self._loop)
                self.sock_writer, _ = await asyncio.wait_for(self._loop.create_pipe_connection(lambda: reader_protocol, ipc_path), self.connection_timeout)
        except FileNotFoundError:
            raise InvalidPipe
        except asyncio.TimeoutError:
            raise ConnectionTimeout

        self.send_data(0, {'v': 1, 'client_id': self.client_id})
        preamble = await self.sock_reader.read(8)
        code, length = struct.unpack('<ii', preamble)
        data = json.loads(await self.sock_reader.read(length))
        if 'code' in data:
            if data['message'] == 'Invalid Client ID':
                raise InvalidID
            raise DiscordError(data['code'], data['message'])
        if self._events_on:
            self.sock_reader.feed_data = self.on_event
