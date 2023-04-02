import typing
from hashlib import sha256

from sqlalchemy import select
from typing import Optional

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        await self.create_admin(
            email=app.config.admin.email, password=app.config.admin.password
        )

    async def get_by_email(self, email: str) -> Optional[Admin]:
        query = select(AdminModel).where(AdminModel.email == email)
        async with self.app.database.session.begin() as session:
            answer = await session.execute(query)
            admin = answer.first()
            if admin:
                return admin[0].to_dc()

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = await self.get_by_email(email)
        if admin:
            return admin

        new_admin = AdminModel(
            email=email, password=sha256(password.encode()).hexdigest()
        )
        async with self.app.database.session.begin() as session:
            session.add(new_admin)
        return new_admin
