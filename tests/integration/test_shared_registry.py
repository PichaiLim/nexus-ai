from hashlib import sha256
import os
from secrets import token_hex
import unittest

from fastapi.testclient import TestClient
import psycopg

from nexus_ai.main import create_app
from nexus_ai.shared_registry import Principal, SharedRegistry


@unittest.skipUnless(os.environ.get("NEXUS_TEST_SHARED_REGISTRY") == "1", "Requires the PostgreSQL integration environment")
class SharedRegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace = f"test-{token_hex(8)}"
        self.other = f"test-{token_hex(8)}"
        principals = []
        self.headers = {}
        for subject, role, workspace in [
            ("owner", "owner", self.workspace), ("agent-a", "reader", self.workspace),
            ("agent-b", "reader", self.workspace), ("outside", "reader", self.other),
        ]:
            token = token_hex(32)
            self.headers[subject] = {"Authorization": f"Bearer {token}"}
            principals.append(Principal(
                workspace=workspace, subject=subject, role=role, token_sha256=sha256(token.encode()).hexdigest(),
            ))
        self.registry = SharedRegistry(os.environ["NEXUS_REGISTRY_DB_HOST"], os.environ["NEXUS_DB_APP_PASSWORD"], principals)
        self.addCleanup(self.clear_workspace)
        self.client = self.enterContext(TestClient(create_app([], registry=self.registry)))
        self.base = f"/api/v1/workspaces/{self.workspace}"

    def clear_workspace(self) -> None:
        with psycopg.connect(**self.registry.store.connection_options) as connection:
            connection.execute("DELETE FROM shared_record_events WHERE workspace=%s", (self.workspace,))
            connection.execute("DELETE FROM shared_records WHERE workspace=%s", (self.workspace,))

    def test_shared_memory_can_be_edited_and_deleted_by_the_owner(self) -> None:
        path = f"{self.base}/memory"
        payload = {"title": "ส่งต่องาน Docker", "content": "เก็บโมเดลเดิมไว้ใน local model stores"}
        self.assertEqual(self.client.get(path).status_code, 401)
        self.assertEqual(self.client.post(path, headers=self.headers["agent-a"], json=payload).status_code, 403)
        created = self.client.post(path, headers=self.headers["owner"], json=payload)
        self.assertEqual(created.status_code, 201, created.text)
        record = created.json()
        detail = f"{path}/{record['id']}"
        self.assertEqual(self.client.get(detail, headers=self.headers["agent-a"]).status_code, 404)
        self.assertEqual(self.client.post(f"{detail}/publish", headers=self.headers["owner"]).status_code, 200)
        result = self.client.get(path, headers=self.headers["agent-a"], params={"q": "LOCAL MODEL"})
        self.assertEqual(result.json()[0]["id"], record["id"])
        thai_result = self.client.get(path, headers=self.headers["agent-b"], params={"q": "เก็บโมเดลเดิม"})
        self.assertEqual(thai_result.json()[0]["title"], payload["title"])
        self.assertEqual(result.headers["Cache-Control"], "no-store")
        self.assertEqual(self.client.get(detail, headers=self.headers["outside"]).status_code, 404)
        self.assertEqual(
            self.client.get(f"/api/v1/workspaces/{self.other}/memory/{record['id']}", headers=self.headers["outside"]).status_code,
            404,
        )
        updated = {**payload, "content": "ใช้คลังโมเดลแบบอ่านอย่างเดียว"}
        self.assertEqual(self.client.put(detail, headers=self.headers["owner"], json=updated).status_code, 200)
        for reader in ("agent-a", "agent-b"):
            response = self.client.get(detail, headers=self.headers[reader])
            self.assertEqual(response.json()["content"], updated["content"])
        self.assertEqual(self.client.delete(detail, headers=self.headers["owner"]).status_code, 204)
        self.assertEqual(self.client.get(detail, headers=self.headers["agent-b"]).status_code, 404)

    def test_skill_versions_are_unique_and_can_be_withdrawn(self) -> None:
        path = f"{self.base}/skills"
        payload = {"title": "UI spacing audit", "content": "Compare browser measurements", "skill_key": "ui-audit", "version": 1}
        created = self.client.post(path, headers=self.headers["owner"], json=payload)
        self.assertEqual(created.status_code, 201, created.text)
        detail = f"{path}/{created.json()['id']}"
        self.assertEqual(self.client.post(path, headers=self.headers["owner"], json=payload).status_code, 409)
        self.assertEqual(self.client.get(detail, headers=self.headers["agent-b"]).status_code, 404)
        self.assertEqual(self.client.post(f"{detail}/publish", headers=self.headers["owner"]).status_code, 200)
        self.assertEqual(self.client.get(detail, headers=self.headers["agent-a"]).json()["version"], 1)
        self.assertEqual(self.client.post(f"{detail}/withdraw", headers=self.headers["agent-b"]).status_code, 403)
        self.assertEqual(self.client.post(f"{detail}/withdraw", headers=self.headers["owner"]).status_code, 200)
        self.assertEqual(self.client.get(detail, headers=self.headers["agent-a"]).status_code, 404)
