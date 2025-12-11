import psycopg2
from pathlib import Path

    
DB_NAME = "nutrition_tracker"
SUPERUSER = "postgres"
PASSWORD = "postgres"
HOST = "localhost"
PORT = 5432

def create_db():
    conn = psycopg2.connect(dbname="postgres", user=SUPERUSER, password=PASSWORD, host=HOST, port=PORT)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{DB_NAME}"')
            cur.execute(f'CREATE DATABASE "{DB_NAME}"')
    finally:
        conn.close()


def delete_alembic_version_scripts():
    versions = Path("alembic/versions")
    for f in versions.glob("*.py"):
        print(f"deleting {f}")
        f.unlink()

def create_alembic_version_scripts():
    import subprocess
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"])

def run_migrations():
    import subprocess
    subprocess.run(["alembic", "upgrade", "head"])

def seed_db():
    import subprocess
    subprocess.run(["python", "-m", "app.database.seed"])

if __name__ == "__main__":
    create_db()
    import time
    time.sleep(2)
    delete_alembic_version_scripts()
    create_alembic_version_scripts()
    run_migrations()
    seed_db()