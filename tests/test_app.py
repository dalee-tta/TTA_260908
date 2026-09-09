import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TodoAppTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ.pop("DATABASE_URL", None)  # 테스트는 항상 SQLite
        os.environ["TODO_DB_PATH"] = os.path.join(self._tmp.name, "test.db")
        import db
        db.reset_init_flag()
        from app import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        os.environ.pop("TODO_DB_PATH", None)
        self._tmp.cleanup()

    # ---- HTML 화면
    def test_index_empty(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("아직 할일이 없습니다", r.get_data(as_text=True))

    def test_add_toggle_edit_delete_via_forms(self):
        r = self.client.post("/add", data={"title": "  우유 사기  "}, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("우유 사기", html)
        self.assertNotIn("  우유 사기  ", html)

        todo = self.client.get("/api/todos").get_json()["todos"][0]
        self.assertFalse(todo["done"])

        self.client.post(f"/toggle/{todo['id']}")
        self.assertTrue(self.client.get(f"/api/todos/{todo['id']}").get_json()["done"])

        self.client.post(f"/edit/{todo['id']}", data={"title": "두유 사기"})
        self.assertEqual(self.client.get(f"/api/todos/{todo['id']}").get_json()["title"], "두유 사기")

        self.client.post(f"/delete/{todo['id']}")
        self.assertEqual(self.client.get(f"/api/todos/{todo['id']}").status_code, 404)

    def test_add_empty_title_shows_error(self):
        r = self.client.post("/add", data={"title": "   "}, follow_redirects=True)
        self.assertIn("할일 내용을 입력해 주세요", r.get_data(as_text=True))
        self.assertEqual(self.client.get("/api/todos").get_json()["counts"]["total"], 0)

    def test_filter_and_clear_done(self):
        self.client.post("/add", data={"title": "A"})
        self.client.post("/add", data={"title": "B"})
        b = self.client.get("/api/todos").get_json()["todos"][0]
        self.client.post(f"/toggle/{b['id']}")

        active = self.client.get("/api/todos?filter=active").get_json()["todos"]
        done = self.client.get("/api/todos?filter=done").get_json()["todos"]
        self.assertEqual([t["title"] for t in active], ["A"])
        self.assertEqual([t["title"] for t in done], ["B"])

        html = self.client.get("/?filter=done").get_data(as_text=True)
        self.assertIn("B", html)
        self.assertNotIn(">A<", html)

        self.client.post("/clear-done")
        counts = self.client.get("/api/todos").get_json()["counts"]
        self.assertEqual(counts, {"total": 1, "done": 0, "active": 1})

    def test_toggle_unknown_id_404(self):
        self.assertEqual(self.client.post("/toggle/9999").status_code, 404)

    # ---- JSON API
    def test_api_crud(self):
        r = self.client.post("/api/todos", json={"title": "API 테스트"})
        self.assertEqual(r.status_code, 201)
        todo = r.get_json()
        self.assertEqual(todo["title"], "API 테스트")

        r = self.client.patch(f"/api/todos/{todo['id']}", json={"done": True, "title": "수정됨"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["title"], "수정됨")
        self.assertTrue(r.get_json()["done"])

        r = self.client.patch(f"/api/todos/{todo['id']}", json={"done": "yes"})
        self.assertEqual(r.status_code, 400)

        r = self.client.delete(f"/api/todos/{todo['id']}")
        self.assertEqual(r.status_code, 204)
        self.assertEqual(self.client.delete(f"/api/todos/{todo['id']}").status_code, 404)

    def test_api_validation(self):
        self.assertEqual(self.client.post("/api/todos", json={}).status_code, 400)
        self.assertEqual(self.client.post("/api/todos", json={"title": "x" * 201}).status_code, 400)
        self.assertEqual(self.client.get("/api/todos?filter=bogus").status_code, 400)

    def test_api_clear_done(self):
        self.client.post("/api/todos", json={"title": "1"})
        r = self.client.post("/api/todos", json={"title": "2"})
        self.client.patch(f"/api/todos/{r.get_json()['id']}", json={"done": True})
        self.assertEqual(self.client.delete("/api/todos/done").get_json()["deleted"], 1)
        self.assertEqual(self.client.get("/api/todos").get_json()["counts"]["total"], 1)

    def test_health(self):
        self.assertEqual(self.client.get("/health").get_json(), {"status": "ok", "database": "sqlite"})


if __name__ == "__main__":
    unittest.main()
