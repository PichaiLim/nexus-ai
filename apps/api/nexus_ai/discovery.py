from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Protocol

import httpx


@dataclass(frozen=True)
class Model:
    id: str
    name: str
    installed: bool | None
    loaded: bool | None
    served: bool | None = None


class Adapter(Protocol):
    async def discover(self, client: httpx.AsyncClient) -> list[Model]: ...


async def rows(client: httpx.AsyncClient, path: str) -> list[dict]:
    response = await client.get(path)
    response.raise_for_status()
    records = response.json()["models"]
    if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
        raise ValueError("Invalid model list")
    return records


class Ollama:
    async def discover(self, client: httpx.AsyncClient) -> list[Model]:
        installed = {row["name"] for row in await rows(client, "/api/tags")}
        loaded = {row["name"] for row in await rows(client, "/api/ps")}
        return [Model(name, name, name in installed, name in loaded)
                for name in sorted(installed | loaded)]


class LMStudio:
    async def discover(self, client: httpx.AsyncClient) -> list[Model]:
        return [Model(row["key"], row["display_name"], True, bool(row["loaded_instances"]))
                for row in await rows(client, "/api/v1/models")]


ADAPTERS: dict[str, Adapter] = {"ollama": Ollama(), "lm-studio": LMStudio()}


@dataclass
class Snapshot:
    models: list[Model]
    synced_at: datetime | None = None
    status: Literal["pending", "ready", "stale", "unreachable"] = "pending"
    error: str | None = None

    def succeeded(self, models: list[Model]) -> None:
        self.models = models
        self.synced_at = datetime.now(timezone.utc)
        self.status = "ready"
        self.error = None

    def failed(self, message: str) -> None:
        self.status = "stale" if self.synced_at else "unreachable"
        self.error = message
