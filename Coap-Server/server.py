import datetime
import logging
import os

import asyncio

import aiocoap.resource as resource
from aiocoap.numbers.contentformat import ContentFormat
import aiocoap

from pathlib import Path

IP_ADRESS = "2600:1900:4150:7757:0:0:0:0"
PORT = 8683

class TemperatureResource(resource.Resource):
    """Resource to put Temperature data to the server. It supports only PUT methods."""

    def __init__(self):
        super().__init__()
        self.set_content(0)

    def set_content(self, content):
        self.content = content

    async def render_put(self, request):
        print('PUT payload: %s' % request.payload)
        self.set_content(request.payload)
        temperature = request.payload # .decode()
        write_temperature_to_file(temperature)
        
        return aiocoap.Message(code=aiocoap.CHANGED)

def set_logger():
    logs_dir = os.path.join(Path(__file__).resolve().parent, "logs")

    if not os.path.exists("logs"):
        os.mkdir(logs_dir)

    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
    logfile = logs_dir + f"/CoAp_server_{current_time}.log"
    print(logfile)

    logging.basicConfig(filename=logfile,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    logging.debug("Logger set up")

    return logging.getLogger('')

def write_temperature_to_file(temperature):
    data_dir = os.path.join(Path(__file__).resolve().parent, "data")

    if not os.path.exists("data"):
        os.mkdir(data_dir)
    
    current_time = datetime.datetime.now().strftime('%Y-%m-%d')
    temperatureFile = data_dir + f"/temperature_{current_time}.txt"
    f = open(temperatureFile, "a")

    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
    f.write(f"{current_time},{temperature}\n")
    f.close()
    
async def main():
    set_logger()
    
    # Resource tree creation
    root = resource.Site()

    root.add_resource(['.well-known', 'core'],
            resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['temperature'], TemperatureResource())

    await aiocoap.Context.create_server_context(root, bind=(IP_ADRESS, PORT))

    # Run forever
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
