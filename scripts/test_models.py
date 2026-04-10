import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.db.session import SessionLocal
from app.db.models import SourceDocument

db = SessionLocal()

try:
    count = db.query(SourceDocument).count()
    print(f"SourceDocument rows: {count}")
finally:
    db.close()