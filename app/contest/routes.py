import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.contest.views import GetContests, SetContestStatus, DeleteContestMembers

    app.router.add_view("/contests", GetContests)
    app.router.add_view("/contest.status", SetContestStatus)
    app.router.add_view("/members.delete", DeleteContestMembers)
