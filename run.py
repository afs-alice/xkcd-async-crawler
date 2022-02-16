import time
from src.xkcd_async_downloader import XkcdAsyncDownloader


def main() -> None:
    start = time.perf_counter()
    instance = XkcdAsyncDownloader()
    instance.make_download()
    print('End of execution!')
    print(f'Resume: {instance.get_amout_of_saved_files}'
          ' comics image files has been downloaded and saved '
          f'in {instance.DIRECTORY}/')
    print('Execution time: {:.2f}s'.format(time.perf_counter() - start))


if __name__ == '__main__':
    main()
