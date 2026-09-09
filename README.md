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
`db.py` 가 환경변수를 보고 백엔드를 자동 선택합니다.

| 조건 | 백엔드 | 용도 |
|---|---|---|
| `DATABASE_URL` 설정됨 | PostgreSQL (Supabase) | 운영(Vercel) |
| 미설정 | SQLite (`todo.db`, `TODO_DB_PATH` 로 경로 변경) | 로컬 개발·테스트 |

`/health` 응답의 `database` 필드로 현재 어떤 백엔드가 쓰이는지 확인할 수 있습니다.

### Supabase 연결
Vercel 서버리스는 IPv4 전용이므로 **트랜잭션 풀러(포트 6543)** 주소를 사용합니다.
```
DATABASE_URL=postgresql://postgres.<ref>:<password>@<region>.pooler.supabase.com:6543/postgres?sslmode=require
```
테이블은 첫 요청 시 `CREATE TABLE IF NOT EXISTS` 로 자동 생성되며, 트랜잭션 풀러 호환을 위해
psycopg 의 서버측 prepared statement 는 비활성화되어 있습니다.

## 배포
- GitHub `main` 푸시 → Vercel 자동 배포
- 프로덕션: https://tta260908ver-three.vercel.app
