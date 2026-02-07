from sqlalchemy import text
from app.database.database import get_engine

def list_tables():
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        return [row[0] for row in result]

def reset_db():
    engine = get_engine()
    
    # Drop all tables
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result]
        
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        
         # Drop all custom ENUM types
        result = conn.execute(text("""
            SELECT t.typname
            FROM pg_type t
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            WHERE t.typtype = 'e' AND n.nspname = 'public'
        """))
        types = [row[0] for row in result]
        
        for enum_type in types:
            conn.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE"))
        
        conn.commit()
    
    print(f"Dropped {len(tables)} tables: {tables}")
    print("\nRun 'alembic upgrade head' to recreate tables")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_db()
    else:
        print("Tables:", list_tables())