from scrapper.openfoodfacts import raspagem_catalogo_produtos, raspar_urls_produtos
from rocketry import Rocketry
from rocketry.conds import after_fail, retry, after_success
import logging

# configura os logs
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
task_logger = logging.getLogger('rocketry.task')
task_logger.addHandler(handler)

app = Rocketry()


# @app.task('daily after 01', name='task-scrapper', retry=10)
@app.task('every 1h')
async def task_raspagem_catalogo_produtos():
    await raspagem_catalogo_produtos(3)


@app.task(after_fail(task_raspagem_catalogo_produtos))
def task_comunicar():
    print('comunicar erro')


@app.task(after_success(task_raspagem_catalogo_produtos))
async def task_raspar_urls_produtos():
    """Raspas as urls com o status Draft"""
    await raspar_urls_produtos()


app.run()
