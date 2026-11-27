import unittest

import httpx
from fastapi.testclient import TestClient

from nexus_ai.main import Source, create_app


class ModelSourcesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.ollama_available = True
        self.calls: list[tuple[str, str]] = []
        sources = [
            Source(id="ollama", name="Local Ollama", engine="ollama", url="http://ollama:11434"),
            Source(id="lm", name="Local LM Studio", engine="lm-studio", url="http://lm:1234"),
        ]
        self.client = TestClient(create_app(sources, httpx.MockTransport(self.runtime)))
        self.client.headers["X-Nexus-Request"] = "1"
        self.addCleanup(self.client.close)

    def runtime(self, request: httpx.Request) -> httpx.Response:
        self.calls.append((request.method, request.url.path))
        if request.url.host == "ollama" and not self.ollama_available:
            raise httpx.ConnectError("offline", request=request)
        records = {
            "/api/tags": [{"name": "same-id"}, {"name": "installed-only"}],
            "/api/ps": [{"name": "same-id"}],
            "/api/v1/models": [{"key": "same-id", "display_name": "LM Model", "loaded_instances": []}],
        }
        return httpx.Response(200, json={"models": records[request.url.path]})

    def test_sync_preserves_source_identity_and_reports_load_state(self) -> None:
        ollama = self.client.post("/api/v1/model-sources/ollama/sync").json()
        lm = self.client.post("/api/v1/model-sources/lm/sync").json()
        self.assertEqual((ollama["id"], lm["id"]), ("ollama", "lm"))
        models = {model["id"]: model for model in ollama["snapshot"]["models"]}
        self.assertTrue(models["same-id"]["loaded"])
        self.assertTrue(models["installed-only"]["installed"])
        self.assertFalse(models["installed-only"]["loaded"])
        self.assertEqual(lm["snapshot"]["models"][0]["id"], "same-id")
        self.assertFalse(lm["snapshot"]["models"][0]["loaded"])
        self.assertTrue(all(method == "GET" for method, _ in self.calls))

    def test_failed_resync_preserves_snapshot_and_other_source_can_sync(self) -> None:
        path = "/api/v1/model-sources/ollama/sync"
        first = self.client.post(path).json()["snapshot"]
        self.ollama_available = False
        stale = self.client.post(path).json()["snapshot"]
        self.assertEqual(stale["status"], "stale")
        self.assertEqual(stale["synced_at"], first["synced_at"])
        self.assertEqual(stale["models"], first["models"])
        self.assertEqual(self.client.post("/api/v1/model-sources/lm/sync").json()["snapshot"]["status"], "ready")

    def test_list_has_no_network_side_effect_and_unknown_source_is_rejected(self) -> None:
        self.assertEqual(len(self.client.get("/api/v1/model-sources").json()), 2)
        self.assertEqual(self.client.post("/api/v1/model-sources/unknown/sync").status_code, 404)
        self.assertEqual(self.calls, [])

    def test_connection_reports_unreachable_without_changing_snapshot(self) -> None:
        self.ollama_available = False
        self.assertEqual(self.client.post("/api/v1/model-sources/ollama/test").status_code, 502)
        self.assertEqual(self.client.get("/api/v1/model-sources").json()[0]["snapshot"]["status"], "pending")


if __name__ == "__main__":
    unittest.main()
