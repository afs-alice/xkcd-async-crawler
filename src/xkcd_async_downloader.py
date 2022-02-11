import asyncio
import logging
import os

import aiofiles
import aiohttp

from contextlib import contextmanager
from hashlib import md5
from typing import Union


class XkcdAsyncDownloader:
    DIRECTORY: str = 'comics-xkcd'
    URL_API: str = 'https://xkcd.com/{}/info.0.json'
    TIMEOUT: int = 30

    def __init__(self) -> None:
        logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.WARNING)
        self.__count_of_saved_files = 0

    @property
    def get_amout_of_saved_files(self):
        return self.__count_of_saved_files

    def make_download(self) -> None:
        if not self._create_directory():
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__create_tasks_of_downloader())
        loop.close()

    async def __create_tasks_of_downloader(self):
        timeout = aiohttp.ClientTimeout(total=self.TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            last_index = await self.__get_last_index(session)
            if not last_index:
                return

            tasks = [self.__task_of_downloader(i, session) for i in range(1, last_index + 1)]
            await asyncio.gather(*tasks)

    async def __task_of_downloader(self, comic_id: int, session: aiohttp.client.ClientSession) -> None:
        comic_image_url = await self.__get_image_comic_url(comic_id, session)
        if not comic_image_url:
            return

        image_file_data = await self.__get_image_file(comic_id, comic_image_url, session)
        if not image_file_data:
            return

        await self.__save_file_in_local_storage(comic_id, image_file_data['content'],
                                                image_file_data['extension'])

    async def __get_image_file(self, comic_id: int, image_url: str,
                               session: aiohttp.client.ClientSession) -> Union[bool, dict]:
        try:
            response_img_file = await session.request('GET', image_url)
        except Exception as e:
            logging.warning((
                f'Error {type(e).__name__} in request for comic id image file: {comic_id}')
            )
            return False

        if response_img_file.status is not 200:
            logging.warning(
                f'Error {response_img_file.status} in request for comic id image file: {comic_id}'
            )
            return False

        if not response_img_file.headers['Content-type'].startswith('image'):
            logging.warning(f'The file for comic id: {comic_id} is not a image')
            return False

        image_file_data = {
            'content': await response_img_file.read(),
            'extension': response_img_file.headers['Content-type'].split('/')[1]
        }
        return image_file_data

    async def __get_image_comic_url(self, comic_id: int,
                                    session: aiohttp.client.ClientSession) -> Union[bool, str]:
        try:
            response_img_url = await session.request('GET', self.URL_API.format(comic_id))
        except Exception as e:
            logging.warning(f'Error {type(e).__name__} in request for comic id image file: {comic_id}')
            return False

        if response_img_url.status is not 200:
            logging.warning(
                f'Error {response_img_url.status} in request for comic id image file: {comic_id}'
            )
            return False

        json = await response_img_url.json()
        image_url = json['img']
        comic_title = json['title']
        logging.info(
            f'URL from image comic id: {comic_id}, title: {comic_title}, has been obtained from API'
        )
        return image_url

    async def __get_last_index(self, session: aiohttp.client.ClientSession) -> Union[bool, int]:
        try:
            response_last_index = await session.request('GET', self.URL_API.format(''))
        except Exception as e:
            logging.error(
                f'Error {type(e).__name__} in request last comic index from xkcd API'
            )
            return False

        if response_last_index.status is not 200:
            logging.error(f'Error {response_last_index.status} when getting last comic index from xkcd API')
            return False

        json = await response_last_index.json()
        last_index = json['num']
        logging.info(f'Last comic index (comic id): {last_index}')
        return last_index

    async def __save_file_in_local_storage(self, comic_id: int, file_content: bytes,
                                           file_extension: str) -> bool:
        file_name = f'{md5(file_content).hexdigest()}.{file_extension}'
        file_path = f'{self.DIRECTORY}/{file_name}'

        if os.path.isfile(file_path):
            logging.info(f'File of comic id: {comic_id} alredy exits with name: {file_name}')
            return False

        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
        except Exception as e:
            logging.error(
                f'Error {type(e).__name__} when save file image for '
                f'comic id: {comic_id} with path: {file_path}'
            )
            return False

        logging.info(f'Comic id: {comic_id} has been saved with name: {file_name}')
        self.__count_of_saved_files += 1
        return True

    def _create_directory(self) -> bool:
        try:
            os.mkdir(self.DIRECTORY)
        except FileExistsError:
            logging.info(f'The directory: "{self.DIRECTORY}/" already exists')
            return True
        except Exception as e:
            logging.error(f'{type(e).__name__} when create directory "{self.DIRECTORY}/"')
            return False
        else:
            logging.info(f'The directory: "{self.DIRECTORY}/" has been created')
            return True
