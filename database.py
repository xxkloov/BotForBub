import aiosqlite
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import asyncio

DB_FILE = "reports.db"
REPORTS_FILE = "reports.json"
DATABASE_URL = os.getenv("DATABASE_URL", "")

USE_POSTGRES = DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")

if USE_POSTGRES:
    try:
        import asyncpg
        POSTGRES_AVAILABLE = True
    except ImportError:
        POSTGRES_AVAILABLE = False
        USE_POSTGRES = False
else:
    POSTGRES_AVAILABLE = False

async def get_db_connection():
    if USE_POSTGRES and POSTGRES_AVAILABLE:
        return await asyncpg.connect(DATABASE_URL)
    else:
        return await aiosqlite.connect(DB_FILE)

async def init_database():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL,
                reported_id INTEGER NOT NULL,
                abuse_type TEXT NOT NULL,
                additional_info TEXT,
                timestamp INTEGER NOT NULL,
                server_id TEXT,
                place_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_reported_id ON reports(reported_id)
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_reporter_id ON reports(reporter_id)
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON reports(timestamp)
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_abuse_type ON reports(abuse_type)
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_user_id INTEGER NOT NULL UNIQUE,
                added_by INTEGER,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_user_id ON admin_users(discord_user_id)
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admin_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL
            )
        """)
        
        await db.commit()

async def migrate_json_to_db():
    if not os.path.exists(REPORTS_FILE):
        return
    
    try:
        with open(REPORTS_FILE, 'r') as f:
            reports = json.load(f)
        
        if not reports:
            return
        
        async with aiosqlite.connect(DB_FILE) as db:
            for report in reports:
                await db.execute("""
                    INSERT OR IGNORE INTO reports 
                    (reporter_id, reported_id, abuse_type, additional_info, timestamp, server_id, place_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.get('reporterId', 0),
                    report.get('reportedId', 0),
                    report.get('abuseType', 'Unknown'),
                    report.get('additionalInfo', ''),
                    report.get('timestamp', int(datetime.now().timestamp())),
                    report.get('serverId', ''),
                    report.get('placeId', 0)
                ))
            
            await db.commit()
        
        backup_file = f"{REPORTS_FILE}.backup"
        if not os.path.exists(backup_file):
            with open(backup_file, 'w') as f:
                json.dump(reports, f, indent=2)
        
    except Exception as e:
        print(f"[database] Error migrating JSON to database: {e}")

async def add_report(reporter_id: int, reported_id: int, abuse_type: str, 
                     additional_info: str, timestamp: int, server_id: str, place_id: int) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("""
            INSERT INTO reports 
            (reporter_id, reported_id, abuse_type, additional_info, timestamp, server_id, place_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (reporter_id, reported_id, abuse_type, additional_info, timestamp, server_id, place_id))
        
        await db.commit()
        return cursor.lastrowid

async def get_reports_last_24h(reported_id: int) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        now = datetime.now().timestamp()
        day_ago = now - 86400
        
        cursor = await db.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE reported_id = ? AND timestamp >= ?
        """, (reported_id, day_ago))
        
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_reports_last_month(reported_id: int) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        now = datetime.now().timestamp()
        month_ago = now - (86400 * 30)
        
        cursor = await db.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE reported_id = ? AND timestamp >= ?
        """, (reported_id, month_ago))
        
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_reporter_history(reporter_id: int) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE reporter_id = ?
        """, (reporter_id,))
        
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_time_since_last_report(reported_id: int, exclude_timestamp: Optional[int] = None) -> Optional[str]:
    async with aiosqlite.connect(DB_FILE) as db:
        if exclude_timestamp:
            cursor = await db.execute("""
                SELECT timestamp FROM reports 
                WHERE reported_id = ? AND timestamp != ?
                ORDER BY timestamp DESC LIMIT 1
            """, (reported_id, exclude_timestamp))
        else:
            cursor = await db.execute("""
                SELECT timestamp FROM reports 
                WHERE reported_id = ?
                ORDER BY timestamp DESC LIMIT 1
            """, (reported_id,))
        
        result = await cursor.fetchone()
        if not result or not result[0]:
            return None
        
        latest_time = result[0]
        time_diff = datetime.now().timestamp() - latest_time
        
        if time_diff < 60:
            return f"{int(time_diff)} seconds ago"
        elif time_diff < 3600:
            return f"{int(time_diff / 60)} minutes ago"
        elif time_diff < 86400:
            return f"{int(time_diff / 3600)} hours ago"
        else:
            return f"{int(time_diff / 86400)} days ago"

async def get_most_common_reason(reported_id: int, exclude_timestamp: Optional[int] = None) -> Optional[str]:
    async with aiosqlite.connect(DB_FILE) as db:
        if exclude_timestamp:
            cursor = await db.execute("""
                SELECT abuse_type, COUNT(*) as count FROM reports 
                WHERE reported_id = ? AND timestamp != ?
                GROUP BY abuse_type
                ORDER BY count DESC LIMIT 1
            """, (reported_id, exclude_timestamp))
        else:
            cursor = await db.execute("""
                SELECT abuse_type, COUNT(*) as count FROM reports 
                WHERE reported_id = ?
                GROUP BY abuse_type
                ORDER BY count DESC LIMIT 1
            """, (reported_id,))
        
        result = await cursor.fetchone()
        if not result:
            return None
        
        return f"{result[0]} ({result[1]} times)"

async def get_reports_by_user(user_id: int, limit: int = 10) -> List[Dict]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM reports 
            WHERE reported_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_recent_reports(limit: int = 10) -> List[Dict]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM reports 
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def search_reports(search_term: str, limit: int = 20) -> List[Dict]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        search_pattern = f"%{search_term}%"
        cursor = await db.execute("""
            SELECT * FROM reports 
            WHERE abuse_type LIKE ? OR additional_info LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (search_pattern, search_pattern, limit))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_report_stats() -> Dict:
    async with aiosqlite.connect(DB_FILE) as db:
        total_reports = await db.execute("SELECT COUNT(*) FROM reports")
        total_result = await total_reports.fetchone()
        total_count = total_result[0] if total_result else 0
        
        today_reports = await db.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE timestamp >= ?
        """, (datetime.now().timestamp() - 86400,))
        today_result = await today_reports.fetchone()
        today_count = today_result[0] if today_result else 0
        
        unique_reported = await db.execute("SELECT COUNT(DISTINCT reported_id) FROM reports")
        unique_result = await unique_reported.fetchone()
        unique_count = unique_result[0] if unique_result else 0
        
        top_abuse = await db.execute("""
            SELECT abuse_type, COUNT(*) as count FROM reports 
            GROUP BY abuse_type
            ORDER BY count DESC LIMIT 1
        """)
        top_result = await top_abuse.fetchone()
        top_abuse_type = f"{top_result[0]} ({top_result[1]})" if top_result else "N/A"
        
        return {
            "total_reports": total_count,
            "today_reports": today_count,
            "unique_reported": unique_count,
            "top_abuse_type": top_abuse_type
        }

async def is_admin(discord_user_id: int) -> bool:
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("""
            SELECT COUNT(*) FROM admin_users 
            WHERE discord_user_id = ?
        """, (discord_user_id,))
        
        result = await cursor.fetchone()
        return (result[0] if result else 0) > 0

async def add_admin(discord_user_id: int, added_by: Optional[int] = None) -> bool:
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                INSERT OR IGNORE INTO admin_users (discord_user_id, added_by)
                VALUES (?, ?)
            """, (discord_user_id, added_by))
            await db.commit()
            return True
    except Exception:
        return False

async def remove_admin(discord_user_id: int) -> bool:
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute("""
                DELETE FROM admin_users WHERE discord_user_id = ?
            """, (discord_user_id,))
            await db.commit()
            return cursor.rowcount > 0
    except Exception:
        return False

async def get_all_admins() -> List[Dict]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM admin_users 
            ORDER BY added_at DESC
        """)
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def create_admin_session(session_token: str, expires_at: datetime) -> bool:
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                INSERT INTO admin_sessions (session_token, expires_at)
                VALUES (?, ?)
            """, (session_token, expires_at))
            await db.commit()
            return True
    except Exception:
        return False

async def validate_admin_session(session_token: str) -> bool:
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("""
            SELECT COUNT(*) FROM admin_sessions 
            WHERE session_token = ? AND expires_at > datetime('now')
        """, (session_token,))
        
        result = await cursor.fetchone()
        return (result[0] if result else 0) > 0

async def cleanup_expired_sessions():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            DELETE FROM admin_sessions 
            WHERE expires_at <= datetime('now')
        """)
        await db.commit()

async def get_most_reported_players(limit: int = 10) -> List[Dict]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT 
                reported_id,
                COUNT(*) as report_count,
                MAX(timestamp) as last_report_time
            FROM reports
            GROUP BY reported_id
            ORDER BY report_count DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_reports_by_abuse_type() -> List[Dict]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT 
                abuse_type,
                COUNT(*) as count
            FROM reports
            GROUP BY abuse_type
            ORDER BY count DESC
        """)
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_reports_today() -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        now = datetime.now().timestamp()
        day_start = now - 86400
        
        cursor = await db.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE timestamp >= ?
        """, (day_start,))
        
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_reports_this_week() -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        now = datetime.now().timestamp()
        week_start = now - (86400 * 7)
        
        cursor = await db.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE timestamp >= ?
        """, (week_start,))
        
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_reports_this_month() -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        now = datetime.now().timestamp()
        month_start = now - (86400 * 30)
        
        cursor = await db.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE timestamp >= ?
        """, (month_start,))
        
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_recent_reports_detailed(limit: int = 20) -> List[Dict]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM reports 
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_reports_by_hour() -> List[Dict]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT 
                strftime('%H', datetime(timestamp, 'unixepoch')) as hour,
                COUNT(*) as count
            FROM reports
            WHERE timestamp >= ?
            GROUP BY hour
            ORDER BY hour
        """, (datetime.now().timestamp() - 86400,))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_top_reporters(limit: int = 10) -> List[Dict]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT 
                reporter_id,
                COUNT(*) as report_count
            FROM reports
            GROUP BY reporter_id
            ORDER BY report_count DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

