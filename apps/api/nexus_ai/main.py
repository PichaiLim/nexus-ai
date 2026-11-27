import asyncio
import json
import os
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, HttpUrl, field_validator

from .discovery import ADAPTERS, Model, Snapshot


class Source(BaseModel):
    id: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{0,62}$")]
    name: Annotated[str, Field(min_length=1, max_length=100)]
    engine: str
    url: HttpUrl
    token_env: Annotated[str, Field(pattern=r"^NEXUS_SOURCE_[A-Z0-9_]+_TOKEN$")] | None = None

    @field_validator("engine")
    @classmethod
    def supported_engine(cls, value: str) -> str:
        if value not in ADAPTERS:
            raise ValueError("Unsupported runtime")
        return value

    @field_validator("url")
    @classmethod
    def base_url(cls, value: HttpUrl) -> HttpUrl:
        if value.username or value.password or value.query or value.fragment or value.path not in ("", "/"):
            raise ValueError("Provide an HTTP(S) origin")
        return value

    def client(self, transport: httpx.AsyncBaseTransport | None) -> httpx.AsyncClient:
        token = os.environ.get(self.token_env) if self.token_env else None
        if self.token_env and not token:
            raise ValueError("Configured source credential is unavailable")
        return httpx.AsyncClient(
            base_url=str(self.url), headers={"Authorization": f"Bearer {token}"} if token else {},
            timeout=5, follow_redirects=False, trust_env=False, transport=transport,
        )


def create_app(
    sources: list[Source],
    transport: httpx.AsyncBaseTransport | None = None,
) -> FastAPI:
    app = FastAPI(title="Nexus AI Model Sources")
    registry = {source.id: source for source in sources}
    if len(registry) != len(sources):
        raise ValueError("Source IDs must be unique")
    snapshots = {source.id: Snapshot([]) for source in sources}
    sync_locks = {source.id: asyncio.Lock() for source in sources}

    def source_by_id(source_id: str) -> Source:
        if source_id not in registry:
            raise HTTPException(404, "Model source not found")
        return registry[source_id]

    def view(source: Source) -> dict:
        return {"id": source.id, "name": source.name, "engine": source.engine,
                "url": str(source.url), "snapshot": snapshots[source.id]}

    async def discover(source: Source) -> list[Model]:
        try:
            async with asyncio.timeout(12), source.client(transport) as client:
                return await ADAPTERS[source.engine].discover(client)
        except httpx.HTTPStatusError as exc:
            raise HTTPException(502, f"Source returned HTTP {exc.response.status_code}") from exc
        except (TimeoutError, httpx.TimeoutException) as exc:
            raise HTTPException(504, "Source timed out") from exc
        except httpx.RequestError as exc:
            raise HTTPException(502, "Source is unreachable") from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise HTTPException(502, "Check source configuration and runtime API compatibility") from exc

    async def require_request_header(x_nexus_request: Annotated[str | None, Header()] = None) -> None:
        if x_nexus_request != "1":
            raise HTTPException(403, "Missing Nexus request header")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/model-sources")
    async def list_sources() -> list[dict]:
        return [view(source) for source in sources]

    @app.post("/api/v1/model-sources/{source_id}/test", dependencies=[Depends(require_request_header)])
    async def test_connection(source_id: str) -> dict[str, str]:
        await discover(source_by_id(source_id))
        return {"status": "reachable"}

    @app.post("/api/v1/model-sources/{source_id}/sync", dependencies=[Depends(require_request_header)])
    async def sync(source_id: str) -> dict:
        source = source_by_id(source_id)
        async with sync_locks[source_id]:
            snapshot = snapshots[source_id]
            try:
                snapshot.succeeded(await discover(source))
            except HTTPException as exc:
                snapshot.failed(str(exc.detail))
            return view(source)

    return app


app = create_app([
    Source.model_validate(source)
    for source in json.loads(
        os.environ.get("NEXUS_MODEL_SOURCES") or os.environ.get("NEXUS_DEFAULT_MODEL_SOURCES", "[]")
    )
])
