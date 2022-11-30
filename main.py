from live_wallpaper import set_latest_as_wallpaper
from rocketry import Rocketry
from rocketry.conds import every
from structlog import getLogger
from datetime import datetime

app = Rocketry()
logger = getLogger()


# @app.task(every("15 minutes"))
# def task():
#     """Set the wallpaper live."""

@app.task('every 15 minutes')
def task():
    set_latest_as_wallpaper('meteosat-11')
    now = datetime.now().strftime('%H:%M:%S')
    logger.msg(time=now, msg='wallpaper changed')


if __name__ == '__main__':
    app.run()
