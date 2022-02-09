from distutils import extension
from time import perf_counter
import aiofiles
import aiohttp
import asyncio
import os
import logging
from hashlib import md5

from contextlib import contextmanager

DIRECTORY = 'comics-xkcd'

async def download_comic(index: int, client: aiohttp.ClientSession):
    with get_except() as captured_except:
        response = await client.request('GET', 'https://xkcd.com/{}/info.0.json'.format(index))
    if captured_except():
        logging.warning(f'Error {type(captured_except()).__name__} in request comic id: {index} from xkcd API')
        return
    if response.status is not 200:
        logging.warning(f'Error {response.status} in xkcd API request from comic id: {index}')
        return

    api_json = await response.json()
    img_url = api_json['img']
    comic_title = api_json['title']
    logging.info(f'URL from image comic id: {index}, title: {comic_title}, has been obtained from xkcd API')

    with get_except() as captured_except:
        response = await client.request('GET', img_url)
    if captured_except():
        logging.warning(f'Error {type(captured_except()).__name__} in request for comic id image file: {index}')
        return
    if response.status is not 200:
        logging.warning(f'Error {response.status} in request for comic id image file: {index}')
        return
    if not response.headers['Content-type'].startswith('image'):
        logging.warning(f'The file for comic id: {index} is not a image')

    extension = response.headers['Content-type'].split('/')[1]
    file_content = await response.read()
    file_name = f'{md5(file_content).hexdigest()}.{extension}'
    file_path = f'{DIRECTORY}/{file_name}'
    if os.path.isfile(file_path):
        logging.info(f'File of Comic id: {index} alredy exits with name: {file_name}')
        return
   
    with get_except() as captured_except:
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

    if captured_except():
        logging.error(f'Error {type(captured_except()).__name__} when save file image for comic id: {index} with path: {file_path}')
        return

    logging.info(f'Comic id: {index} has been saved with name: {file_name}')

@contextmanager
def get_except():
    is_except = None
    try:
        yield lambda: is_except
    except Exception as captured_except:
        is_except = captured_except

async def main():
    import time
    start = perf_counter()
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
        return
    
    async with aiohttp.ClientSession() as session:
        with get_except() as captured_except:            
            response = await session.request('GET', 'https://xkcd.com/{}/info.0.json'.format(''))
        if captured_except():
            logging.warning(f'Error {type(captured_except()).__name__} in request last comic index from xkcd API')
            return
        if(response.status != 200):
            logging.warning(f'Error {response.status} when getting last comic index from xkcd API')
            return
        api_json = await response.json()
        last_index = api_json['num']
        logging.info(f'Last comic index (comic id): {last_index}')
        
        tasks = []
        for i in range(1, last_index+1):
            tasks.append(asyncio.create_task(download_comic(i, session)))
        await asyncio.gather(*tasks)
    end = perf_counter()
    print(end - start)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
