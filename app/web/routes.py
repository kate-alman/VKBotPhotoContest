from aiohttp.web_app import Application


def setup_routes(app: Application):
    from app.admin.routes import setup_routes as admin_setup_routes
    from app.contest.routes import setup_routes as contest_setup_routes

    admin_setup_routes(app)
    contest_setup_routes(app)
