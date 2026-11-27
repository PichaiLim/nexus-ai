from pathlib import Path
from uuid import UUID

import psycopg
from psycopg.rows import dict_row


class SharedStore:
    def __init__(self, host: str, password: str) -> None:
        self.connection_options = dict(
            host=host, dbname="nexus_ai", user="nexus_app", password=password, connect_timeout=4,
        )

    async def connect(self) -> psycopg.AsyncConnection:
        return await psycopg.AsyncConnection.connect(
            **self.connection_options, row_factory=dict_row, options="-c statement_timeout=5000",
        )

    async def initialize(self) -> None:
        sql = Path(__file__).with_name("shared_schema.sql").read_text(encoding="utf-8")
        async with await self.connect() as connection:
            await connection.execute("SELECT pg_advisory_xact_lock(430021)")
            await connection.execute(sql)

    async def list_records(
        self, connection: psycopg.AsyncConnection, workspace: str, kind: str,
        owner: str | None, q: str, limit: int, offset: int,
    ) -> list[dict]:
        cursor = await connection.execute(
            """SELECT id, title, source, skill_key, version, visibility, updated_at
               FROM shared_records
               WHERE workspace=%s AND kind=%s AND (visibility='published' OR owner=%s)
                 AND strpos(lower(title || ' ' || content), lower(%s)) > 0
               ORDER BY updated_at DESC, id LIMIT %s OFFSET %s""",
            (workspace, kind, owner, q, limit, offset),
        )
        return await cursor.fetchall()

    async def read(
        self, connection: psycopg.AsyncConnection, workspace: str, kind: str, record_id: UUID, owner: str | None,
    ) -> dict | None:
        cursor = await connection.execute(
            """SELECT * FROM shared_records WHERE workspace=%s AND kind=%s AND id=%s
               AND (visibility='published' OR owner=%s)""",
            (workspace, kind, record_id, owner),
        )
        return await cursor.fetchone()

    async def insert(
        self, connection: psycopg.AsyncConnection, workspace: str, kind: str, record_id: UUID, owner: str,
        *, title: str, content: str, source: str | None, skill_key: str | None, version: int | None,
    ) -> dict | None:
        cursor = await connection.execute(
            """INSERT INTO shared_records (id, workspace, kind, owner, title, content, source, skill_key, version)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
            (record_id, workspace, kind, owner, title, content, source, skill_key, version),
        )
        return await cursor.fetchone()

    async def update_memory(
        self, connection: psycopg.AsyncConnection, workspace: str, record_id: UUID, owner: str,
        *, title: str, content: str, source: str | None,
    ) -> dict | None:
        cursor = await connection.execute(
            """UPDATE shared_records SET title=%s, content=%s, source=%s, updated_at=now()
               WHERE workspace=%s AND kind='memory' AND id=%s AND owner=%s RETURNING *""",
            (title, content, source, workspace, record_id, owner),
        )
        return await cursor.fetchone()

    async def set_visibility(
        self, connection: psycopg.AsyncConnection, workspace: str, kind: str, record_id: UUID,
        owner: str, previous: str, visibility: str,
    ) -> dict | None:
        cursor = await connection.execute(
            """UPDATE shared_records SET visibility=%s, updated_at=now()
               WHERE workspace=%s AND kind=%s AND id=%s AND owner=%s AND visibility=%s RETURNING *""",
            (visibility, workspace, kind, record_id, owner, previous),
        )
        return await cursor.fetchone()

    async def delete_memory(
        self, connection: psycopg.AsyncConnection, workspace: str, record_id: UUID, owner: str,
    ) -> dict | None:
        cursor = await connection.execute(
            "DELETE FROM shared_records WHERE workspace=%s AND kind='memory' AND id=%s AND owner=%s RETURNING id",
            (workspace, record_id, owner),
        )
        return await cursor.fetchone()

    async def record_event(
        self, connection: psycopg.AsyncConnection, workspace: str, actor: str, record_id: UUID, action: str,
    ) -> None:
        await connection.execute(
            "INSERT INTO shared_record_events (workspace, record_id, actor, action) VALUES (%s, %s, %s, %s)",
            (workspace, record_id, actor, action),
        )
