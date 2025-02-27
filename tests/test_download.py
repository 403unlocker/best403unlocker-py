import requests
import math
import time
from datetime import datetime


def test_convert_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0B"

    size_units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

    count_of_1024 = int (math.log(size_bytes, 1024))
    complete_number = int (math.pow(1024, count_of_1024))
    size_bytes /= complete_number

    return f"{size_bytes:.2f} {size_units[count_of_1024]}"


def test_download_file(url: str, file_path: str = '', packet_size_byte: int = 20480):
    # checks connection => response = 200
    response = requests.get(url, stream=True)
    # give error if it is not accessible
    response.raise_for_status()

    # Get the total file size
    total_size = int(response.headers.get('content-length', 0))


    # os date & time
    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path += date

    # create download file for writing in binary
    with open(file_path, 'wb') as file:
        print(f'File size: {test_convert_size(total_size)}')

        size = 0
        x1 = time.time()
        # downloads packet
        for chunk in response.iter_content(chunk_size=packet_size_byte):
            if chunk:
                # write packet to file
                file.write(chunk)


                # load download size
                size += len(chunk)
                x2 = time.time()

                spend_time = x2 - x1

               # load download speed
                speed = size / spend_time

                print(f'\rDownloaded: {test_convert_size(size)}, Speed: {test_convert_size(speed)}/s', end='')

    print(f'\n\nDownload Complete\nFile Name Save: {file_path}')
