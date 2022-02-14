import asyncio
import unittest

from os import path, rmdir, remove
from src.xkcd_async_downloader import XkcdAsyncDownloader
from unittest.mock import patch, mock_open

def async_test(coro):
    def wrapped(*args, **kwargs):
        try:
            asyncio.run(coro(*args, **kwargs))
        except InterruptedError:
            pass
    return wrapped

class TestCreateDirectory(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.instance.DIRECTORY = 'directory_of_test'

    def tearDown(self) -> None:
        try:
            rmdir(self.instance.DIRECTORY)
        except:
            pass
    
    def test_create_directory(self):
        self.instance._XkcdAsyncDownloader__create_directory()
        self.assertTrue(path.isdir(self.instance.DIRECTORY))
        

    @patch('os.mkdir')
    def test_displays_info_log_msg_when_directory_has_been_created(self, mock_mkdir):
        mock_mkdir.side_effect = None
        with self.assertLogs() as captured_log:
            self.instance._XkcdAsyncDownloader__create_directory()
        self.assertEqual(captured_log.output[0], f'INFO:root:The directory: "{self.instance.DIRECTORY}/" '
                                                 'has been created')

    @patch('os.mkdir')
    def test_displays_info_log_msg_when_directory_alredy_exists(self, mock_mkdir):
        mock_mkdir.side_effect = FileExistsError
        with self.assertLogs() as captured_log:
            self.instance._XkcdAsyncDownloader__create_directory()
        self.assertEqual(captured_log.output[0], f'INFO:root:The directory: "{self.instance.DIRECTORY}/" '
                                                 'already exists')

    @patch('os.mkdir')
    def test_displays_error_log_msg_when_exceptions_are_raised(self, mock_mkdir):
        exceptions = [OSError, PermissionError, FileNotFoundError]
        for expt in exceptions:
            mock_mkdir.side_effect = expt
            with self.assertLogs() as captured_log:
                self.instance._XkcdAsyncDownloader__create_directory()
            self.assertEqual(captured_log.output[0], f'ERROR:root:{expt.__name__} when create directory '
                                                     f'"{self.instance.DIRECTORY}/"')


class TestSaveFileInLocalStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.instance.DIRECTORY = '.'
        with open('test/src/fixtures/img_file.png', 'rb') as img_file:
            self.file_data = {
                'content': img_file.read(),
                'extension': 'png'
            }
        self.comic_id = 2579
        self.md5_img_name_file = '2f00e94162e4023b0270a3f309588075.png'
        self.file_path = f'{self.instance.DIRECTORY}/{self.md5_img_name_file}'
    
    def tearDown(self) -> None:
        try:
            remove(self.md5_img_name_file)
        except:
            pass
    
    @async_test   
    async def test_create_img_file_named_with_md5(self):
        await self.instance._XkcdAsyncDownloader__save_file_in_local_storage(
            self.comic_id, self.file_data['content'], self.file_data['extension']
        )
        self.assertTrue(path.isfile(self.md5_img_name_file))
    
    @async_test
    @patch('builtins.open', new_callable=mock_open())
    async def test_display_info_log_msg_when_file_has_been_created(self, mock_open):
        mock_open.side_effect = None
        with self.assertLogs() as captured_log:
            await self.instance._XkcdAsyncDownloader__save_file_in_local_storage(
                self.comic_id, self.file_data['content'], self.file_data['extension']
            )
        self.assertEqual(captured_log.output[0], f'INFO:root:Comic id: {self.comic_id} has been saved with '
                                                 f'name: {self.md5_img_name_file}')

    @async_test
    @patch('builtins.open', new_callable=mock_open())
    async def test_display_info_log_msg_when_exceptions_are_raised(self, mock_open):
        known_execptions = [IsADirectoryError, PermissionError, FileNotFoundError]
        for exeption in known_execptions:
            mock_open.side_effect = exeption
            with self.assertLogs() as captured_log:
                 await self.instance._XkcdAsyncDownloader__save_file_in_local_storage(
                    self.comic_id, self.file_data['content'], self.file_data['extension']
                 )
            self.assertEqual(captured_log.output[0], f'Error {exeption.__name__} when save file image for '
                                                     f'comic id: {self.comic_id} with '
                                                     f'path: {self.file_path}')

    @async_test
    @patch('builtins.open', new_callable=mock_open())
    async def test_increment_count_of_saved_files_attribute_when_file_has_been_saved(self, mock_open):
        mock_open.side_effect = None
        await self.instance._XkcdAsyncDownloader__save_file_in_local_storage(
            self.comic_id, self.file_data['content'], self.file_data['extension']
        )
        self.assertEqual(1, self.instance._XkcdAsyncDownloader__count_of_saved_files)
        


if __name__ == '__main__':
    unittest.main()