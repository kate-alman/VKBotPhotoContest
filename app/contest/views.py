from aiohttp.web_response import Response
from aiohttp_apispec import request_schema, response_schema, docs

from app.contest.schemes import (
    GetContestSchema,
    ResponseGetContestSchema,
    ContestSchema,
    SetContestStatusSchema,
    ResponseContestSchema,
    DeleteMembersSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class GetContests(AuthRequiredMixin, View):
    @docs(
        tags=["contest"],
        summary="List contests",
        description="Get current list contests from database",
    )
    @request_schema(GetContestSchema)
    @response_schema(ResponseGetContestSchema, 200)
    async def get(self) -> Response:
        contests_list = await self.store.contest.get_contests(
            self.data.get("is_active", None)
        )
        if contests_list:
            data_contests = [ContestSchema().dump(contest) for contest in contests_list]
            return json_response(data=data_contests)
        return json_response(data="No matching contests")


class SetContestStatus(AuthRequiredMixin, View):
    @docs(
        tags=["contest"],
        summary="Set contest status",
        description="Set active/inactive contest",
    )
    @request_schema(SetContestStatusSchema)
    @response_schema(ResponseContestSchema, 200)
    async def post(self) -> Response:
        chat_id = self.data["chat_id"]
        status = self.data["is_active"]
        contest = await self.store.contest.get_contest_by_id(chat_id)
        if contest:
            await self.store.contest.rerun_contest(
                chat_id
            ) if status else await self.store.contest.set_inactive_contest(
                chat_id, None
            )
            return json_response(data=ResponseContestSchema().dump(contest))
        return json_response(data="No matching contests")


class DeleteContestMembers(AuthRequiredMixin, View):
    @docs(
        tags=["contest"],
        summary="Delete members",
        description="Delete members from database",
    )
    @request_schema(DeleteMembersSchema)
    @response_schema(ResponseContestSchema, 200)
    async def post(self) -> Response:
        chat_id = self.data["chat_id"]
        contest = await self.store.contest.get_contest_by_id(chat_id)
        if contest:
            await self.store.contest.delete_members(chat_id)
            return json_response(data=ResponseContestSchema().dump(contest))
        return json_response(data="No matching contests")
