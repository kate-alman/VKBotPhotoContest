from aiohttp.web import HTTPForbidden
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_response import Response
from aiohttp_apispec import request_schema, response_schema, docs
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema, AdminRequestSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=["admin"], summary="Admin login", description="Admin login")
    @request_schema(AdminRequestSchema)
    @response_schema(AdminSchema, 200)
    async def post(self) -> Response:
        email = self.data["email"]
        password = self.data["password"]

        admin_from_db = await self.store.admins.get_by_email(email)

        if not admin_from_db:
            raise HTTPForbidden(text="Access is denied")
        if not admin_from_db.is_password_valid(password):
            raise HTTPBadRequest(text="Invalid password")

        admin_data = AdminSchema().dump(admin_from_db)
        session = await new_session(request=self.request)
        session["admin"] = admin_data
        return json_response(data=admin_data)


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=["admin"], summary="Current admin", description="Current admin")
    @response_schema(AdminSchema, 200)
    async def get(self) -> Response:
        return json_response(data=AdminSchema().dump(self.request.admin))
