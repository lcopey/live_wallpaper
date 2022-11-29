import ctypes
import io
import json
from builtins import bytes
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import requests
from PIL import Image


def requests_get(url: str) -> Optional[bytes]:
    """Get request at specified url."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.content


def get_image(content: bytes) -> np.array:
    """Convert bytes content into np.array representing a PIL Image."""
    img = Image.open(io.BytesIO(content))
    img = np.array(img)
    return img


def get_border_url(row: int, col: int, date: Union[int, datetime], scale: int = 2,
                   satellite: str = 'meteosat-11') -> str:
    """Format the url to get border outline of country."""
    # if isinstance(date, datetime):
    #     time_url = date.strftime('%Y/%m/%d')
    # else:
    #     time_url = datetime.strptime(str(date), "%Y%m%d%H%M%S").strftime('%Y/%m/%d')
    # contour
    url = (f"""https://rammb-slider.cira.colostate.edu/data/maps/"""
           f"""{satellite}/full_disk/borders/white/19700101010000/"""
           f"""{scale:02d}/{row:03d}_{col:03d}.png""")
    return url


def get_planet_url(row: int, col: int, date: Union[int, datetime], scale: int = 2,
                   satellite: str = 'meteosat-11') -> str:
    """Format the url to get satellite image."""
    if not isinstance(date, datetime):
        # time_url = date.strftime('%Y/%m/%d')
        date = datetime.strptime(str(date), "%Y%m%d%H%M%S")
        time_url = date.strftime('%Y/%m/%d')
    else:
        time_url = date.strftime('%Y/%m/%d')
        date = date.strftime("%Y%m%d%H%M%S")

    url = ("""https://rammb-slider.cira.colostate.edu/data/imagery/"""
           f"""{time_url}/{satellite}---full_disk/geocolor/{date}/"""
           f"""{scale:02d}/{row:03d}_{col:03d}.png""")
    return url


def get_image_from(mode: str, row: int, col: int, date: Union[int, datetime],
                   scale: int = 2, satellite: str = 'meteosat-11') -> Optional[np.array]:
    """Get the image from rammb website."""
    url = URLS[mode](row, col, date, scale=scale, satellite=satellite)
    content = requests_get(url)
    if content is not None:
        img = get_image(content)
        return img


def get_dates(satellite: str = 'meteosat-11') -> List[datetime]:
    """Get available date for the corresponding satellite."""
    url = f'https://rammb-slider.cira.colostate.edu/data/json/{satellite}/full_disk/natural_color/latest_times.json'
    content = requests_get(url)
    json_values = json.loads(content)["timestamps_int"]
    dates = [datetime.strptime(str(date), "%Y%m%d%H%M%S") for date in json_values]
    dates.sort()
    return dates


def stitch_image(mode: str, date: Union[int, datetime], scale: int, satellite: str = 'meteosat-11') -> Image:
    """Get the mozaic images and stitch them together."""
    intermediate = []
    raw = []
    for row in range(8):
        for col in range(8):
            row_img = get_image_from(mode, row, col, date, scale=scale, satellite=satellite)
            if row_img is not None:
                raw.append(row_img)
        intermediate.append(np.hstack(raw))
        raw = []
    final_image = np.vstack(intermediate)
    final_image = Image.fromarray(final_image)
    return final_image


def latest_as_png(file_path: str, satellite='meteosat-11'):
    dates = get_dates(satellite=satellite)
    img = stitch_image('planet', dates[-1], scale=3, satellite=satellite)
    img.save(file_path)


def set_as_wallpaper(satellite='meteosat-11'):
    path = './earth.png'
    latest_as_png(path, satellite=satellite)
    ABS_PATH = str(Path(path).absolute())
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, ABS_PATH, 3)


URLS = {'planet': get_planet_url, 'border': get_border_url}
