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

    # async def make_download(self, session: aiohttp.ClientSession) -> None:
    #     with self.__get_except() as captured_except:
    #         response = await session.request('GET', self.URL_API.format((index)))
    #     if captured_except():
    #         logging.warning(f'Error {type(captured_except()).__name__} in request comic id: {index} from xkcd API')
    #         return
    #     if response.status is not 200:
    #         logging.warning(f'Error {response.status} in xkcd API request from comic id: {index}')
    #         return
    async def saved_file_in_local_storage(self, file_content: bytes, file_extension: str) -> Any:
        file_name = f'{md5(file_content).hexdigest()}.{file_extension}'
        file_path = f'{self.DIRECTORY}/{file_name}'
        if os.path.isfile(file_path):
            logging.info(f'File {file_name} alredy exits')
        return
        with self.__get_except() as captured_except:
            async with aiofiles.open(file_name, 'wb') as f:
                await f.write(file_content)
        return captured_except
    
    async def make_async_request(self, url: str) -> aiohttp.ClientSession():
        with self.__get_except() as captured_except:            
            return await session.request('GET', url)
        return captured_except

    def __create_directory(self) -> bool:
        with self.__get_except() as captured_except:
            os.mkdir(self.DIRECTORY)
            
        if not captured_except():
            logging.info(f'The directory: "{self.DIRECTORY}/" has been created')
        elif isinstance(captured_except(), FileExistsError):
            logging.info(f'The directory: "{self.DIRECTORY}/" already exists')
        else:
            logging.error(f'{type(captured_except()).__name__} when create directory "{self.DIRECTORY}/"')
            return

    @contextmanager
    def __get_except(self):
        is_except = None
        try:
            yield lambda: is_except
        except Exception as captured_except:
            is_except = captured_except

instance = XkcdAsyncDownloader()
instance._XkcdAsyncDownloader__create_directory()