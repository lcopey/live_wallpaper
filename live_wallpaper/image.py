from asyncio import ensure_future, gather
from datetime import datetime
from io import BytesIO
from typing import Iterable, Union
import requests

import numpy as np
from aiohttp import ClientSession
from PIL import Image


def get_border_url(row: int, col: int, date: Union[int, datetime], scale: int = 2,
                   satellite: str = 'meteosat-11') -> str:
    """Format the url to get border outline of country."""
    url = (f"""https://rammb-slider.cira.colostate.edu/data/maps/"""
           f"""{satellite}/full_disk/borders/white/19700101010000/"""
           f"""{scale:02d}/{row:03d}_{col:03d}.png""")
    return url


def get_planet_url(row: int, col: int, date: Union[int, datetime], scale: int = 2,
                   satellite: str = 'meteosat-11') -> str:
    """Format the url to get satellite image."""
    if not isinstance(date, datetime):
        date = datetime.strptime(str(date), "%Y%m%d%H%M%S")
        time_url = date.strftime('%Y/%m/%d')
    else:
        time_url = date.strftime('%Y/%m/%d')
        date = date.strftime("%Y%m%d%H%M%S")

    url = ("""https://rammb-slider.cira.colostate.edu/data/imagery/"""
           f"""{time_url}/{satellite}---full_disk/geocolor/{date}/"""
           f"""{scale:02d}/{row:03d}_{col:03d}.png""")
    return url


URLS = {'planet': get_planet_url, 'border': get_border_url}


async def async_get_single_image(session: ClientSession, url: str):
    """Asynchronously get image from url"""
    async with session.get(url) as resp:
        content = await resp.read()
        return content


async def async_get_image_patches(mode: str,
                                  date: Union[int, datetime],
                                  scale: int,
                                  satellite: str = 'meteosat-11') -> Iterable[Iterable['Image']]:
    """Asynchronously get all images patch from satellite."""
    async with ClientSession() as session:
        row_count = 8
        col_count = 8
        tasks = []
        for row in range(row_count):
            for col in range(col_count):
                url = URLS[mode](row, col, date, scale, satellite)
                tasks.append(ensure_future(async_get_single_image(session, url)))

        images = await gather(*tasks)
        images = [[Image.open(BytesIO(images[i + n])) for n in range(col_count)]
                  for i in range(0, col_count * row_count, col_count)]
        return images


def get_single_image(url: str):
    """Asynchronously get image from url"""
    response = requests.get(url)
    if response.status_code == 200:
        return response.content


def get_image_patches(mode: str,
                      date: Union[int, datetime],
                      scale: int,
                      satellite: str = 'meteosat-11') -> Iterable[Iterable['Image']]:
    """Asynchronously get all images patch from satellite."""
    row_count = 8
    col_count = 8
    images = []
    for row in range(row_count):
        for col in range(col_count):
            url = URLS[mode](row, col, date, scale, satellite)
            images.append(get_single_image(url))

    images = [[Image.open(BytesIO(images[i + n])) for n in range(col_count)]
              for i in range(0, col_count * row_count, col_count)]
    return images


def stitch_images(images: Iterable[Iterable['Image']]) -> Image:
    """Stitch images together."""
    image = Image.fromarray(
        np.vstack(
            [np.hstack([np.array(img) for img in row])
             for row in images]
        )
    )
    return image
