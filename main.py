from live_wallpaper import set_latest_as_wallpaper
from rocketry import Rocketry
from rocketry.conds import every

app = Rocketry()


@app.task(every("15 minutes"))
def task():
    """Set the wallpaper live."""
    set_latest_as_wallpaper('meteosat-11')


if __name__ == '__main__':
    app.run()
