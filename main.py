from live_wallpaper import set_latest_as_wallpaper
from rocketry import Rocketry
from structlog import getLogger
from datetime import datetime
import asyncio

app = Rocketry()
logger = getLogger()


@app.task('every 15 minutes')
def task():
    now = datetime.now().strftime('%H:%M:%S')
    print(f'{now}, changing')
    set_latest_as_wallpaper('meteosat-11')
    now = datetime.now().strftime('%H:%M:%S')
    print(f'{now}, done')
    # logger.msg(time=now, msg='done')


#
# async def main():
#     rocketry_task = asyncio.create_task(app.serve())
#     await rocketry_task


if __name__ == '__main__':
    app.run()
    # asyncio.run(main())
    # set_latest_as_wallpaper('meteosat-11')
