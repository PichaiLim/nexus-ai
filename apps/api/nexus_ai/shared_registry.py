from collections.abc import AsyncIterator
from hashlib import sha256
import json
import os
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import psycopg
from pydantic import BaseModel, Field, StringConstraints

from .shared_store import SharedStore


Kind = Literal["memory", "skills"]
Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{0,62}$")]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Content = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30000)]


class Principal(BaseModel):
    workspace: Slug
    subject: Slug
    role: Literal["owner", "reader"]
    token_sha256: Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]


class RecordInput(BaseModel):
    title: ShortText
    content: Content
    source: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)] | None = None


class CreateRecord(RecordInput):
    skill_key: Slug | None = None
    version: Annotated[int, Field(ge=1, le=2147483647)] | None = None


def configured_principals() -> list[Principal]:
    principals = [Principal.model_validate(item) for item in json.loads(os.environ.get("NEXUS_SHARED_PRINCIPALS", "[]"))]
    for role in ("owner", "reader"):
        token = os.environ.get(f"NEXUS_SHARED_{role.upper()}_TOKEN")
        if token:
            principals.append(Principal(
                workspace="local", subject=f"local-{role}", role=role,
                token_sha256=sha256(token.encode()).hexdigest(),
            ))
    return principals


class SharedRegistry:
    def __init__(self, host: str, password: str, principals: list[Principal]) -> None:
        self.store = SharedStore(host, password)
        self.principals = {principal.token_sha256: principal for principal in principals}
        if len(self.principals) != len(principals):
            raise ValueError("Shared registry credentials must be unique")

    async def initialize(self) -> None:
        await self.store.initialize()

    def router(self) -> APIRouter:
        router = APIRouter(prefix="/api/v1/workspaces/{workspace}", tags=["Shared registry"])
        bearer = HTTPBearer(auto_error=False)

        async def authenticate(
            workspace: Slug,
            credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
        ) -> Principal:
            principal = self.principals.get(sha256(credentials.credentials.encode()).hexdigest()) if credentials else None
            if principal is None:
                raise HTTPException(401, "Valid workspace credentials required", headers={"WWW-Authenticate": "Bearer"})
            if principal.workspace != workspace:
                raise HTTPException(404, "Workspace not found")
            return principal

        async def require_owner(principal: Annotated[Principal, Depends(authenticate)]) -> Principal:
            if principal.role != "owner":
                raise HTTPException(403, "Owner access required")
            return principal

        async def connect() -> AsyncIterator[psycopg.AsyncConnection]:
            try:
                async with await self.store.connect() as connection:
                    yield connection
            except psycopg.OperationalError as exc:
                raise HTTPException(503, "Shared registry is unavailable") from exc

        reader = Depends(authenticate)
        owner = Depends(require_owner)
        db = Depends(connect, scope="function")

        async def record_event(connection: psycopg.AsyncConnection, principal: Principal, record_id: UUID, action: str) -> None:
            await self.store.record_event(connection, principal.workspace, principal.subject, record_id, action)

        def found(row: dict | None) -> dict:
            if row is None:
                raise HTTPException(404, "Record not found")
            return row

        @router.get("/{kind}")
        async def list_records(
            kind: Kind,
            principal: Principal = reader,
            connection: psycopg.AsyncConnection = db,
            q: Annotated[str, Query(max_length=200)] = "",
            offset: Annotated[int, Query(ge=0, le=10000)] = 0,
            limit: Annotated[int, Query(ge=1, le=100)] = 25,
        ) -> list[dict]:
            return await self.store.list_records(
                connection, principal.workspace, kind, principal.subject if principal.role == "owner" else None,
                q, limit, offset,
            )

        @router.get("/{kind}/{record_id}")
        async def read_record(
            kind: Kind, record_id: UUID, principal: Principal = reader, connection: psycopg.AsyncConnection = db,
        ) -> dict:
            row = await self.store.read(
                connection, principal.workspace, kind, record_id, principal.subject if principal.role == "owner" else None,
            )
            return found(row)

        @router.post("/{kind}", status_code=201)
        async def create_record(
            kind: Kind, payload: CreateRecord, principal: Principal = owner, connection: psycopg.AsyncConnection = db,
        ) -> dict:
            if kind == "skills" and (payload.skill_key is None or payload.version is None):
                raise HTTPException(422, "Skills require skill_key and version")
            if kind == "memory" and (payload.skill_key is not None or payload.version is not None):
                raise HTTPException(422, "Memory does not accept skill version fields")
            record_id = uuid4()
            try:
                row = await self.store.insert(
                    connection, principal.workspace, kind, record_id, principal.subject, **payload.model_dump(),
                )
            except psycopg.errors.UniqueViolation as exc:
                raise HTTPException(409, "Skill version already exists") from exc
            await record_event(connection, principal, record_id, "create")
            return found(row)

        @router.put("/memory/{record_id}")
        async def update_memory(
            record_id: UUID, payload: RecordInput, principal: Principal = owner, connection: psycopg.AsyncConnection = db,
        ) -> dict:
            row = found(await self.store.update_memory(
                connection, principal.workspace, record_id, principal.subject, **payload.model_dump(),
            ))
            await record_event(connection, principal, record_id, "update")
            return row

        @router.post("/{kind}/{record_id}/{action}")
        async def set_visibility(
            kind: Kind, record_id: UUID, action: Literal["publish", "withdraw"],
            principal: Principal = owner, connection: psycopg.AsyncConnection = db,
        ) -> dict:
            visibility, previous = ("published", "draft") if action == "publish" else ("withdrawn", "published")
            row = found(await self.store.set_visibility(
                connection, principal.workspace, kind, record_id, principal.subject, previous, visibility,
            ))
            await record_event(connection, principal, record_id, action)
            return row

        @router.delete("/memory/{record_id}", status_code=204)
        async def delete_memory(
            record_id: UUID, principal: Principal = owner, connection: psycopg.AsyncConnection = db,
        ) -> Response:
            found(await self.store.delete_memory(connection, principal.workspace, record_id, principal.subject))
            await record_event(connection, principal, record_id, "delete")
            return Response(status_code=204)

        return router
