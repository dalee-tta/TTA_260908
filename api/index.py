"""Vercel 서버리스 진입점. 프로젝트 루트의 Flask 앱을 그대로 노출한다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402,F401
