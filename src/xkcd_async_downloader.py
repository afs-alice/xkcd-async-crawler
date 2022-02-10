import time
import aiofiles
import asyncio
import logging

import aiohttp 
from contextlib import contextmanager
from hashlib import md5
import os

class XkcdAsyncDownloader():
    DIRECTORY : str = 'comics-xkcd'
    URL_API : str = 'https://xkcd.com/{}/info.0.json'
    TIMEOUT : int = 10

    def __init__(self) -> None:
        logging.basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.INFO)
   
    def make_download(self):
        if not self.__create_directory():
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__create_tasks_of_comic_downloader())
        loop.close()

    async def __create_tasks_of_comic_downloader(self):
        async with aiohttp.ClientSession() as session:
            last_index = await self.__get_last_index(session)
            if not last_index:
                return
            tasks = []
            for index in range(1, last_index + 1):
                tasks.append(self.__task_of_downloader(index, session))
            await asyncio.gather(*tasks)
                
    async def __task_of_downloader(self, comic_id: int, session: aiohttp.client.ClientSession) -> dict:
        comic_image_url = await self.__get_image_comic_url(comic_id, session)
        if not comic_image_url:
            return
        image_file_data = await self.__get_image_file(comic_id, comic_image_url, session)
        if not image_file_data:
            return
        if not await self.__save_file_in_local_storage(comic_id, image_file_data['content'], image_file_data['extension']):
            return

    async def __get_image_file(self, comic_id: int, image_url: str, session: aiohttp.client.ClientSession):
        with self.__get_except() as captured_except:            
            response_img_file = await session.request('GET', image_url)
        if captured_except():
            logging.warning(f'Error {type(captured_except()).__name__} in request for comic id image file: {comic_id}')
        if response_img_file.status is not 200:
            logging.warning(f'Error {response_img_file.status} in request for comic id image file: {comic_id}')
        if not response_img_file.headers['Content-type'].startswith('image'):
            logging.warning(f'The file for comic id: {comic_id} is not a image')
        else:
            image_file_data = {
                'content': await response_img_file.read(),
                'extension': response_img_file.headers['Content-type'].split('/')[1]
            }
            return image_file_data
        return False


    async def __get_image_comic_url(self, comic_id: int, session: aiohttp.client.ClientSession)  -> str:
        with self.__get_except() as captured_except:            
            response_img_url = await session.request('GET', self.URL_API.format(comic_id))
        if captured_except():
            logging.warning(f'Error {type(captured_except()).__name__} in request for comic id image file: {comic_id}')
            return False
        elif response_img_url.status is not 200:
            logging.warning(f'Error {response_img_url.status} in request for comic id image file: {comic_id}')
            return False
        else:
            json = await response_img_url.json()
            image_url = json['img']
            comic_title = json['title']
            logging.info(f'URL from image comic id: {comic_id}, title: {comic_title}, has been obtained from API')
            return image_url

    async def __get_last_index(self, session: aiohttp.client.ClientSession) -> int:
        with self.__get_except() as captured_except:            
            response_last_index = await session.request('GET', self.URL_API.format(''))
        if captured_except():
            logging.error(f'Error {type(captured_except().__name__)} in request last comic index from xkcd API')
        elif response_last_index.status is not 200:
            logging.error(f'Error {response_last_index.status} when getting last comic index from xkcd API')
        else:
            json = await response_last_index.json()
            last_index = json['num']
            logging.info(f'Last comic index (comic id): {last_index}')
            return last_index
        return False

    async def __save_file_in_local_storage(self, comic_id: int, file_content: bytes, file_extension: str) -> bool:
        file_name = f'{md5(file_content).hexdigest()}.{file_extension}'
        file_path = f'{self.DIRECTORY}/{file_name}'
        if os.path.isfile(file_path):
            logging.info(f'File of comic id: {comic_id} alredy exits with name: {file_name}')
            return False
        with self.__get_except() as captured_except:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
        if captured_except():
            logging.error(f'Error {type(captured_except()).__name__} when save file image for comic id: {comic_id} with path: {file_path}')
            return False
        logging.info(f'Comic id: {comic_id} has been saved with name: {file_name}')
        return True

    def __create_directory(self) -> bool:
        with self.__get_except() as captured_except:
            os.mkdir(self.DIRECTORY)
            
        if not captured_except():
            logging.info(f'The directory: "{self.DIRECTORY}/" has been created')   
        elif isinstance(captured_except(), FileExistsError):
            logging.info(f'The directory: "{self.DIRECTORY}/" already exists')
        else:
            logging.error(f'{type(captured_except()).__name__} when create directory "{self.DIRECTORY}/"')
            return False
        return True

    @contextmanager
    def __get_except(self):
        is_except = None
        try:
            yield lambda: is_except
        except Exception as captured_except:
            is_except = captured_except
import time
start = time.perf_counter()
instance = XkcdAsyncDownloader()
instance.make_download()
print(time.perf_counter() - start)