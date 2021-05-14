import toml
import asyncpg


with open("./config/config.toml") as f:
    database_auth = toml.loads(f.read())["database"]

class DatabaseConnection:

    def __init__(self, conn=None):
        self.conn = conn

    async def connect(self):
        self.conn = await asyncpg.connect(**database_auth)

    async def disconnect(self):
        await self.conn.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()

    async def __call__(self, sql, *args):
        return await self.conn.fetch(sql, *args)
