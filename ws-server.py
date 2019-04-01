import asyncio
import datetime
import json
import websockets
import random


async def stream(websocket, path):
    while True:
        data = json.dumps([
            {
                'instrument': 'IF1901',
                'price': 3000 + random.randint(0, 100)
            },
            {
                'instrument': 'IF1902',
                'price': 3200 + random.randint(0, 100)
            }
        ])
        await websocket.send(data)
        await asyncio.sleep(1)

start_server = websockets.serve(stream, 'localhost', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()