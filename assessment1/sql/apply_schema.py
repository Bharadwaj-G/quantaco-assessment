"""Apply schema.sql and seed.sql to the DB pointed at by env vars / .env.

Run once against a fresh instance (e.g. a local Postgres for development):
    python sql/apply_schema.py
"""

import pathlib
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from database import get_connection  # noqa: E402

SQL_DIR = pathlib.Path(__file__).resolve().parent


def main() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for filename in ("schema.sql", "seed.sql"):
                sql = (SQL_DIR / filename).read_text()
                print(f"Applying {filename}...")
                cur.execute(sql)
        conn.commit()
        print("Done.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
