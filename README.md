# 할일 관리 앱 (Flask)

Python Flask 로 만든 간단한 할일(To-Do) 관리 웹앱입니다.

## 기능
- 할일 추가 / 완료 토글 / 제목 수정 / 삭제
- 전체 · 진행중 · 완료 필터, 완료 항목 일괄 삭제
- JSON API (`/api/todos`) 제공
- JavaScript 없이도 모든 기능이 폼만으로 동작

## 실행
```bash
pip install -r requirements.txt
python app.py
# http://127.0.0.1:5000
```

## 테스트
```bash
python -m unittest discover -s tests -v
```

## API
| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/todos?filter=all\|active\|done` | 목록 + 집계 |
| POST | `/api/todos` `{"title": "..."}` | 생성 (201) |
| GET | `/api/todos/<id>` | 단건 조회 |
| PATCH | `/api/todos/<id>` `{"title"?, "done"?}` | 수정 |
| DELETE | `/api/todos/<id>` | 삭제 (204) |
| DELETE | `/api/todos/done` | 완료 항목 일괄 삭제 |
| GET | `/health` | 상태 확인 |

## 구조
```
todo_app/
├─ app.py            # 라우트
├─ db.py             # 저장소 계층 (SQLite) — DB 교체 시 이 파일만 수정
├─ templates/index.html
├─ static/           # style.css, app.js
├─ tests/test_app.py
├─ api/index.py      # Vercel 서버리스 진입점
└─ vercel.json
```

## 저장소
- 기본: 앱 폴더의 `todo.db` (SQLite)
- 환경변수 `TODO_DB_PATH` 로 경로 변경 가능
- Vercel 환경(`VERCEL` 변수 존재)에서는 `/tmp/todo.db` 사용 — 서버리스 특성상 영구 저장이 아니므로, 운영에서는 외부 DB(Supabase 등) 연결 필요
