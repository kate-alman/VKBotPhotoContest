import os

from aiohttp.web import run_app

from app.web.app import setup_app


app = setup_app()

if __name__ == "__main__":
    run_app(app, host=os.environ['APP_IP'], port=os.environ['APP_PORT'])
