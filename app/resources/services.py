from sqlalchemy.ext.asyncio.engine import AsyncConnection


class DBCursorService:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection
        self.commit = connection.commit
        self.rollback = connection.rollback

    async def execute(self, query, commit: bool = False):
        try:
            result = await self.connection.execute(query)
            if commit:
                await self.commit()
            return result
        except:  # noqa
            await self.rollback()
            raise

    async def scalar(self, query, commit: bool = False):
        return (await self.execute(query, commit)).scalar()

    async def one(self, query, commit: bool = False) -> dict | None:
        row = (await self.execute(query, commit)).fetchone()
        return dict(row) if row else None

    async def many(self, query, commit: bool = False) -> list[dict]:
        return [
            dict(row) for row in (await self.execute(query, commit)).fetchall()
        ]
