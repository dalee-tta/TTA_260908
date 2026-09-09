"""할일 관리 앱 (Flask).

- HTML 화면: /            (폼 기반, JS 없이도 동작)
- JSON API : /api/todos   (프론트엔드·외부 연동용)
"""
from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

import db

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

VALID_FILTERS = ("all", "active", "done")
MAX_TITLE_LEN = 200


@app.before_request
def _ensure_db():
    db.init_db()


def _clean_title(raw: str | None) -> str | None:
    """공백을 정리하고 유효하지 않으면 None을 돌려준다."""
    title = (raw or "").strip()
    if not title or len(title) > MAX_TITLE_LEN:
        return None
    return title


# ---------------------------------------------------------------- HTML 화면
@app.get("/")
def index():
    status = request.args.get("filter", "all")
    if status not in VALID_FILTERS:
        status = "all"
    return render_template(
        "index.html",
        todos=db.list_todos(status),
        counts=db.count_todos(),
        current_filter=status,
        error=request.args.get("error"),
    )


def _back(**params):
    """현재 필터를 유지한 채 목록으로 돌아간다."""
    status = request.form.get("filter") or request.args.get("filter") or "all"
    return redirect(url_for("index", filter=status, **params))


@app.post("/add")
def add():
    title = _clean_title(request.form.get("title"))
    if title is None:
        return _back(error="할일 내용을 입력해 주세요 (최대 200자).")
    db.add_todo(title)
    return _back()


@app.post("/toggle/<int:todo_id>")
def toggle(todo_id: int):
    if db.toggle_todo(todo_id) is None:
        abort(404)
    return _back()


@app.post("/edit/<int:todo_id>")
def edit(todo_id: int):
    title = _clean_title(request.form.get("title"))
    if title is None:
        return _back(error="할일 내용을 입력해 주세요 (최대 200자).")
    if db.update_todo(todo_id, title=title) is None:
        abort(404)
    return _back()


@app.post("/delete/<int:todo_id>")
def delete(todo_id: int):
    if not db.delete_todo(todo_id):
        abort(404)
    return _back()


@app.post("/clear-done")
def clear_done():
    db.clear_done()
    return _back()


# ---------------------------------------------------------------- JSON API
@app.get("/api/todos")
def api_list():
    status = request.args.get("filter", "all")
    if status not in VALID_FILTERS:
        return jsonify(error="filter must be one of all/active/done"), 400
    return jsonify(todos=db.list_todos(status), counts=db.count_todos())


@app.post("/api/todos")
def api_create():
    data = request.get_json(silent=True) or {}
    title = _clean_title(data.get("title"))
    if title is None:
        return jsonify(error="title is required (1~200 chars)"), 400
    return jsonify(db.add_todo(title)), 201


@app.get("/api/todos/<int:todo_id>")
def api_get(todo_id: int):
    todo = db.get_todo(todo_id)
    if todo is None:
        return jsonify(error="not found"), 404
    return jsonify(todo)


@app.patch("/api/todos/<int:todo_id>")
def api_update(todo_id: int):
    data = request.get_json(silent=True) or {}
    title = None
    if "title" in data:
        title = _clean_title(data.get("title"))
        if title is None:
            return jsonify(error="title must be 1~200 chars"), 400
    done = data.get("done")
    if done is not None and not isinstance(done, bool):
        return jsonify(error="done must be boolean"), 400
    todo = db.update_todo(todo_id, title=title, done=done)
    if todo is None:
        return jsonify(error="not found"), 404
    return jsonify(todo)


@app.delete("/api/todos/<int:todo_id>")
def api_delete(todo_id: int):
    if not db.delete_todo(todo_id):
        return jsonify(error="not found"), 404
    return "", 204


@app.delete("/api/todos/done")
def api_clear_done():
    return jsonify(deleted=db.clear_done())


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
