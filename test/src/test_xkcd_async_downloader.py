import unittest

from os import path, rmdir
from src.xkcd_async_downloader import XkcdAsyncDownloader
from unittest.mock import patch, Mock

class TestCreateDirectory(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = XkcdAsyncDownloader()
        self.instance.DIRECTORY = 'directory_of_test'
    
    def test_create_directory(self):
        self.instance._create_directory()
        self.assertTrue(path.isdir(self.instance.DIRECTORY))
        rmdir(self.instance.DIRECTORY)


if __name__ == '__main__':
    unittest.main()