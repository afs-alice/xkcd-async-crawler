import asyncio
import json
import unittest

from os import path, rmdir, remove
from time import sleep
from unittest.mock import patch

from aiohttp.client import ClientSession
from async_class import AsyncClass
from http.client import InvalidURL

from src.xkcd_async_downloader import XkcdAsyncDownloader


def async_test(coroutine):
    def wrapped(*args, **kwargs):
        try:
            asyncio.run(coroutine(*args, **kwargs))
        except InterruptedError:
            pass
    return wrapped


class MockResponse(AsyncClass):
    async def __ainit__(self, status: int = 200, json: dict = {}, read: bytes = b'',
                        headers: dict = {}) -> None:
        self.status = status
        self.headers = headers
        self.json_content = json
        self.read_content = read

    async def json(self):
        sleep(0)
        return self.json_content

    async def read(self):
        sleep(0)
        return self.read_content


def get_api_json_fixture() -> dict:
    with open('src/test/src/fixtures/api_content_file.json') as file:
        return json.loads(file.read())


def get_headers_img_file_fixture() -> dict:
    with open('src/test/src/fixtures/headers_img_file.json') as file:
        return json.loads(file.read())


def get_headers_no_img_file_fixture() -> dict:
    with open('src/test/src/fixtures/headers_no_img_file.json') as file:
        return json.loads(file.read())


def get_img_file_binary_content() -> bytes:
    with open('src/test/src/fixtures/img_file.png', 'rb') as file:
        return file.read()


class TestCreateDirectory(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.instance.DIRECTORY = 'directory_of_test'

    def tearDown(self) -> None:
        try:
            rmdir(self.instance.DIRECTORY)
        except FileNotFoundError:
            pass

    def test_create_directory(self):
        self.instance._XkcdAsyncDownloader__create_directory()
        self.assertTrue(path.isdir(self.instance.DIRECTORY))

    @patch('os.mkdir')
    def test_displays_info_log_msg_when_directory_has_been_created_adn_return_true(self, mock_mkdir):
        mock_mkdir.side_effect = None
        with self.assertLogs() as captured_log:
            method_return = self.instance._XkcdAsyncDownloader__create_directory()
        self.assertEqual(
            captured_log.output[0],
            f'INFO:root:The directory: "{self.instance.DIRECTORY}/" has been created'
        )
        self.assertTrue(method_return)

    @patch('os.mkdir')
    def test_displays_info_log_msg_when_directory_already_exists_and_return_true(self, mock_mkdir):
        mock_mkdir.side_effect = FileExistsError
        with self.assertLogs() as captured_log:
            method_return = self.instance._XkcdAsyncDownloader__create_directory()
        self.assertEqual(
            captured_log.output[0],
            f'INFO:root:The directory: "{self.instance.DIRECTORY}/" already exists'
        )
        self.assertTrue(method_return)

    @patch('os.mkdir')
    def test_displays_error_log_msg_when_exceptions_are_raised_and_return_false(self, mock_mkdir):
        exceptions = [OSError, PermissionError, FileNotFoundError]
        for expt in exceptions:
            mock_mkdir.side_effect = expt
            with self.assertLogs() as captured_log:
                method_return = self.instance._XkcdAsyncDownloader__create_directory()
            self.assertEqual(
                captured_log.output[0],
                f'ERROR:root:{expt.__name__} when create directory "{self.instance.DIRECTORY}/"'
            )
            self.assertFalse(method_return)


class TestSaveFileInLocalStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.instance.DIRECTORY = '.'
        self.file_data = {'content': get_img_file_binary_content(), 'extension': 'png'}
        self.comic_id = 2579
        self.md5_img_name_file = '2f00e94162e4023b0270a3f309588075.png'
        self.file_path = f'{self.instance.DIRECTORY}/{self.md5_img_name_file}'

    def tearDown(self) -> None:
        try:
            remove(self.md5_img_name_file)
        except FileNotFoundError:
            pass

    @async_test
    async def test_create_file_named_with_md5__display_info_log__increment_count_atribute__return_true(self):
        with self.assertLogs() as captured_log:
            captured_return = await self.instance._XkcdAsyncDownloader__save_file_in_local_storage(
                self.comic_id, self.file_data['content'], self.file_data['extension']
            )
        self.assertTrue(path.isfile(self.md5_img_name_file))
        self.assertEqual(
            captured_log.output[0],
            f'INFO:root:Comic id: {self.comic_id} has been saved with name: {self.md5_img_name_file}'
        )
        self.assertEqual(1, self.instance._XkcdAsyncDownloader__count_of_saved_files)
        self.assertTrue(captured_return)

    @patch('os.path.isfile', return_value=True)
    @async_test
    async def test_display_info_log_msg_when_file_already_exists_and_return_none(self, mock_open):
        with self.assertLogs() as captured_log:
            captured_return = await self.instance._XkcdAsyncDownloader__save_file_in_local_storage(
                self.comic_id, self.file_data['content'], self.file_data['extension']
            )
        self.assertEqual(
            captured_log.output[0],
            f'INFO:root:File of comic id: {self.comic_id} already exits with name: {self.md5_img_name_file}'
        )
        self.assertIsNone(captured_return)

    @patch('aiofiles.open')
    @async_test
    async def test_display_error_log_msg_when_exceptions_are_raised_and_return_none(self, mock_open):
        known_exceptions = [IsADirectoryError, PermissionError, FileNotFoundError]
        for exception in known_exceptions:
            mock_open.side_effect = exception
            with self.assertLogs() as captured_log:
                captured_return = await self.instance._XkcdAsyncDownloader__save_file_in_local_storage(
                    self.comic_id, self.file_data['content'], self.file_data['extension']
                )
            self.assertEqual(
                captured_log.output[0],
                f'ERROR:root:Error {exception.__name__} when save file image for '
                f'comic id: {self.comic_id} with path: {self.file_path}'
            )
            self.assertIsNone(captured_return)


class TestGetLastIndex(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.expected_last_index = 2579

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_return_false_and_display_error_log_when_exceptions_are_raised(self, mock_iorequest):
        known_exceptions = [InvalidURL, TimeoutError, ConnectionError]
        for exception in known_exceptions:
            mock_iorequest.side_effect = exception
            with self.assertLogs() as captured_log:
                method_return = await self.instance._XkcdAsyncDownloader__get_last_index(ClientSession())
            self.assertFalse(method_return)
            self.assertEqual(
                captured_log.output[0],
                f'ERROR:root:Error {exception.__name__} in request last comic index from xkcd API'
            )

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_return_false_and_display_error_log_when_status_code_is_not_200(self, mock_iorequest):
        status_codes = [403, 404, 500]
        for code in status_codes:
            mock_iorequest.return_value = MockResponse(status=code)
            with self.assertLogs() as captured_log:
                method_return = await self.instance._XkcdAsyncDownloader__get_last_index(ClientSession())
            self.assertFalse(method_return)
            self.assertEqual(
                captured_log.output[0],
                f'ERROR:root:Error {code} when getting last comic index from xkcd API'
            )

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_return_last_index_and_display_info_log(self, mock_iorequest):
        mock_iorequest.return_value = MockResponse(json=get_api_json_fixture())
        with self.assertLogs() as captured_log:
            method_return = await self.instance._XkcdAsyncDownloader__get_last_index(ClientSession())
        self.assertEqual(captured_log.output[0], f'INFO:root:Last comic index (comic id): {method_return}')
        self.assertEqual(self.expected_last_index, method_return)


class TestGetComicImageUrl(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.image_url = 'https://imgs.xkcd.com/comics/tractor_beam.png'
        self.comic_id = 2579
        self.comic_title = 'Tractor Beam'

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_display_warning_log_and_return_false_when_status_code_is_not_200(self, mock_iorequest):
        status_codes = [403, 404, 500]
        for code in status_codes:
            mock_iorequest.return_value = MockResponse(status=code)
            with self.assertLogs() as captured_log:
                method_return = await self.instance._XkcdAsyncDownloader__get_comic_image_url(
                    self.comic_id, ClientSession()
                )
            self.assertEqual(
                captured_log.output[0],
                f'WARNING:root:Error {code} in request for comic id image file: {self.comic_id}'
            )
            self.assertFalse(method_return)

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_display_error_log_and_return_false_when_exceptions_are_raised(self, mock_iorequest):
        known_exceptions = [InvalidURL, TimeoutError, ConnectionError]
        for exception in known_exceptions:
            mock_iorequest.side_effect = exception
            with self.assertLogs() as captured_log:
                method_return = await self.instance._XkcdAsyncDownloader__get_comic_image_url(
                    self.comic_id, ClientSession()
                )
            self.assertFalse(method_return)
            self.assertEqual(
                captured_log.output[0],
                f'WARNING:root:Error {exception.__name__} in request for comic id image file: {self.comic_id}'
            )

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_return_image_url_and_info_log(self, mock_iorequest):
        mock_iorequest.return_value = MockResponse(json=get_api_json_fixture())
        with self.assertLogs() as captured_log:
            method_return = await self.instance._XkcdAsyncDownloader__get_comic_image_url(
                self.comic_id, ClientSession()
            )
        self.assertEqual(
            captured_log.output[0],
            f'INFO:root:URL from image comic id: {self.comic_id}, title: {self.comic_title}, '
            'has been obtained from API'
        )
        self.assertEqual(self.image_url, method_return)


class TestGetImageFile(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.img_file_content = get_img_file_binary_content()
        self.comic_id = 2579
        self.image_url = 'https://imgs.xkcd.com/comics/tractor_beam.png'
        self.image_file_data = {'content': get_img_file_binary_content(), 'extension': 'png'}
        self.headers = get_headers_img_file_fixture()

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_display_warning_log_and_return_false_when_exceptions_are_raised(self, mock_iorequest):
        known_exceptions = [InvalidURL, TimeoutError, ConnectionError]
        for exception in known_exceptions:
            mock_iorequest.side_effect = exception
            with self.assertLogs() as captured_log:
                method_return = await self.instance._XkcdAsyncDownloader__get_image_file(
                    self.comic_id, self.image_url, ClientSession()
                )
            self.assertFalse(method_return)
            self.assertEqual(
                captured_log.output[0],
                f'WARNING:root:Error {exception.__name__} in request for comic id image file: {self.comic_id}'
            )

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_return_false_and_warning_log_when_status_code_is_not_200(self, mock_iorequest):
        status_codes = [403, 404, 500]
        for code in status_codes:
            mock_iorequest.return_value = MockResponse(status=code)
            with self.assertLogs() as captured_log:
                method_return = await self.instance._XkcdAsyncDownloader__get_image_file(
                    self.comic_id, self.image_url, ClientSession()
                )
            self.assertEqual(
                captured_log.output[0],
                f'WARNING:root:Error {code} in request for comic id image file: {self.comic_id}'
            )
            self.assertFalse(method_return)

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_return_false_and_warning_log_when_content_of_response_is_not_image(self, mock_iorequest):
        mock_iorequest.return_value = MockResponse(headers=get_headers_no_img_file_fixture())
        with self.assertLogs() as captured_log:
            method_return = await self.instance._XkcdAsyncDownloader__get_image_file(
                self.comic_id, self.image_url, ClientSession()
            )
        self.assertEqual(
            captured_log.output[0],
            f'WARNING:root:The file for comic id: {self.comic_id} is not a image'
        )
        self.assertFalse(method_return)

    @patch('aiohttp.client.ClientSession.request')
    @async_test
    async def test_return_image_file_data(self, mock_iorequest):
        mock_iorequest.return_value = MockResponse(read=self.img_file_content, headers=self.headers)
        method_return = await self.instance._XkcdAsyncDownloader__get_image_file(
            self.comic_id, self.image_url, ClientSession()
        )
        self.assertEqual(self.image_file_data, method_return)


class TestTaskOfDownloader(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.session = 'client_session_instance'
        self.comic_id = 2579
        self.image_url = 'https://imgs.xkcd.com/comics/tractor_beam.png'
        self.image_file_data = {'content': get_img_file_binary_content(), 'extension': 'png'}

    async def awaited_return(self, arg=''):
        sleep(0)
        return arg

    @patch.object(XkcdAsyncDownloader, '_XkcdAsyncDownloader__save_file_in_local_storage')
    @patch.object(XkcdAsyncDownloader, '_XkcdAsyncDownloader__get_image_file')
    @patch.object(XkcdAsyncDownloader, '_XkcdAsyncDownloader__get_comic_image_url')
    @async_test
    async def test_call_methods_with_corrects_arguments_and_returns(
        self, mock_get_comic_image_url, mock_get_image_file, mock_save_file_in_local_storage
    ):
        mock_get_comic_image_url.return_value = self.awaited_return(self.image_url)
        mock_get_image_file.return_value = self.awaited_return(self.image_file_data)
        mock_save_file_in_local_storage.return_value = self.awaited_return()
        await self.instance._XkcdAsyncDownloader__task_of_downloader(self.comic_id, self.session)

        mock_get_comic_image_url.assert_called_once_with(self.comic_id, self.session)
        mock_get_image_file.assert_called_once_with(self.comic_id, self.image_url, self.session)
        mock_save_file_in_local_storage.assert_called_once_with(
            self.comic_id, self.image_file_data['content'], self.image_file_data['extension']
        )

    @patch.object(XkcdAsyncDownloader, '_XkcdAsyncDownloader__get_comic_image_url')
    @async_test
    async def test_return_false_when_image_url_is_false(self, mock_get_comic_image_url):
        mock_get_comic_image_url.return_value = self.awaited_return(False)
        method_return = await self.instance._XkcdAsyncDownloader__task_of_downloader(
            self.comic_id, self.session
        )
        self.assertIsNone(method_return)

    @patch.object(XkcdAsyncDownloader, '_XkcdAsyncDownloader__get_image_file')
    @patch.object(XkcdAsyncDownloader, '_XkcdAsyncDownloader__get_comic_image_url')
    @async_test
    async def test_return_false_when_image_file_data_is_false(
        self, mock_get_comic_image_url, mock_get_comic_image_file
    ):
        mock_get_comic_image_url.return_value = self.awaited_return(self.image_url)
        mock_get_comic_image_file.return_value = self.awaited_return(False)
        method_return = await self.instance._XkcdAsyncDownloader__task_of_downloader(
            self.comic_id, self.session
        )
        self.assertIsNone(method_return)


if __name__ == '__main__':
    unittest.main()
