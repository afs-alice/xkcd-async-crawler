import unittest

from os import path, rmdir
from src.xkcd_async_downloader import XkcdAsyncDownloader
from unittest.mock import patch, Mock


class TestCreateDirectory(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.instance.DIRECTORY = 'directory_of_test'
    
    def test_create_directory(self):
        self.instance._XkcdAsyncDownloader__create_directory()
        self.assertTrue(path.isdir(self.instance.DIRECTORY))
        rmdir(self.instance.DIRECTORY)

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

if __name__ == '__main__':
    unittest.main()