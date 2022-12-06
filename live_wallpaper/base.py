import asyncio
import ctypes
import json
from datetime import datetime
from pathlib import Path
from typing import List

import requests

from .image import async_get_image_patches, stitch_images, get_image_patches


def get_dates(satellite: str = 'meteosat-11') -> List[datetime]:
    """Get available date for the corresponding satellite."""
    url = f'https://rammb-slider.cira.colostate.edu/data/json/{satellite}/full_disk/natural_color/latest_times.json'
    response = requests.get(url)
    if response.status_code == 200:
        content = response.content
        # response.json()
        json_values = json.loads(content)["timestamps_int"]
        dates = [datetime.strptime(str(date), "%Y%m%d%H%M%S") for date in json_values]
        dates.sort()
        return dates


def latest_as_png(file_path: str, satellite='meteosat-11'):
    """Get latest image and save it as png."""
    dates = get_dates(satellite=satellite)
    images = get_image_patches('planet', dates[-1], scale=3, satellite=satellite)
    # images = asyncio.run(async_get_image_patches('planet', dates[-1], scale=3, satellite=satellite))
    img = stitch_images(images)
    # img = stitch_image('planet', dates[-1], scale=3, satellite=satellite)
    img.save(file_path)


def set_latest_as_wallpaper(satellite='meteosat-11'):
    """Download the latest image and set it as wallpaper."""
    path = './earth.png'
    latest_as_png(path, satellite=satellite)
    ABS_PATH = str(Path(path).absolute())
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, ABS_PATH, 3)

#
# def get_image_from(mode: str, row: int, col: int, date: Union[int, datetime],
#                    scale: int = 2, satellite: str = 'meteosat-11') -> Optional[np.array]:
#     """Get the image from rammb website."""
#     url = URLS[mode](row, col, date, scale=scale, satellite=satellite)
#     response = requests.get(url)
#     if response.status_code == 200:
#         content = response.content
#         if content is not None:
#             img = Image.open(io.BytesIO(content))
#             img = np.array(img)
#             return img
#
# def stitch_image(mode: str, date: Union[int, datetime], scale: int, satellite: str = 'meteosat-11') -> Image:
#     """Get the mozaic images and stitch them together."""
#     intermediate = []
#     raw = []
#     for row in range(8):
#         for col in range(8):
#             row_img = get_image_from(mode, row, col, date, scale=scale, satellite=satellite)
#             if row_img is not None:
#                 raw.append(row_img)
#         intermediate.append(np.hstack(raw))
#         raw = []
#     final_image = np.vstack(intermediate)
#     final_image = Image.fromarray(final_image)
#     return final_image
#
