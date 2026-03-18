import psycopg2
import psycopg2.extras
from config import Config

def get_db():
    conn = psycopg2.connect(Config.DATABASE_URL)
    conn.autocommit = False
    return conn

def query(sql, params=None, fetch='all'):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        if fetch == 'one':
            result = cur.fetchone()
        elif fetch == 'all':
            result = cur.fetchall()
        else:
            result = None
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute(sql, params=None):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        conn.commit()
        try:
            return cur.fetchone()
        except:
            return None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
