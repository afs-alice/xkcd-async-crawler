import aiofiles
import aiohttp
import asyncio
import os
import logging

from contextlib import contextmanager

DIRECTORY = 'comics-xkcd'

async def download_comic(index: int, client: aiohttp.ClientSession):
    print("iniciando requisição comic id", index)
    response = await client.request('GET', 'https://xkcd.com/{}/info.0.json'.format(index))
    if response.status is not 200:
        return True
    html = await response.json()
    requests = await client.request('GET', html["img"])
    print("baixado comic id: ", html["num"], "title", html["title"])
    image_name = html["img"].split('/')[::-1][0]
    if not image_name:
        return True
    path = f'comics-xkcd/{image_name}'
    async with aiofiles.open(path, 'wb') as f:
        await f.write((await requests.read()))
        # with open(path, 'wb') as f:
        #     f.write(await response.read())
    return


@contextmanager
def get_except():
    is_except = None
    try:
        yield lambda: is_except
    except Exception as expt:
        is_except = expt

async def main():
    logging.basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.INFO)

    with get_except() as captured_except:
        os.mkdir(DIRECTORY)
    
    if not captured_except():
        logging.info(f'The directory: "{DIRECTORY}/" has been created')
    elif isinstance(captured_except(), FileExistsError):
        logging.info(f'The directory: "{DIRECTORY}/" already exists')
    else:
        logging.error(f'{type(captured_except()).__name__} when create directory "{DIRECTORY}/"')
    
    # async with aiohttp.ClientSession() as client:
    #     tasks = []
    #     for i in range(1, 2578):
    #         tasks.append((download_comic(i, client)))

    #     await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
