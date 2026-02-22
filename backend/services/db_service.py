"""
Database Service - SQLite persistence for optimization history and technique effectiveness

Provides:
- Optimization history tracking (all strategies: standard, dgeo, shdt, cdraf)
- Technique effectiveness learning (which techniques work best for which defects)
- Benchmark results storage

Uses SQLite (zero-config, ships with Python, no external dependencies).
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

from ..utils import get_logger
from ..config import Config

logger = get_logger(__name__)

# Database path: store in project data/ directory
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "promptoptimizer.db")


def _ensure_db_dir():
    """Ensure the data directory exists"""
    os.makedirs(DB_DIR, exist_ok=True)


@contextmanager
def get_connection():
    """Get a database connection with automatic cleanup"""
    _ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist"""
    _ensure_db_dir()
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_prompt TEXT NOT NULL,
                optimized_prompt TEXT NOT NULL,
                strategy TEXT NOT NULL DEFAULT 'standard',
                score_before REAL NOT NULL,
                score_after REAL NOT NULL,
                improvement REAL NOT NULL,
                defects_before TEXT,
                defects_after TEXT,
                techniques_applied TEXT,
                evolution_history TEXT,
                trajectory_history TEXT,
                critique_history TEXT,
                metadata TEXT,
                task_type TEXT DEFAULT 'general',
                domain TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS technique_effectiveness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                technique_id TEXT NOT NULL,
                defect_id TEXT NOT NULL,
                times_applied INTEGER DEFAULT 0,
                total_improvement REAL DEFAULT 0.0,
                avg_improvement REAL DEFAULT 0.0,
                success_count INTEGER DEFAULT 0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(technique_id, defect_id)
            );

            CREATE TABLE IF NOT EXISTS benchmark_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                benchmark_id TEXT NOT NULL,
                strategy TEXT NOT NULL,
                score_before REAL,
                score_after REAL,
                improvement REAL,
                defects_fixed INTEGER DEFAULT 0,
                processing_time_ms INTEGER,
                cost REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_history_strategy ON optimization_history(strategy);
            CREATE INDEX IF NOT EXISTS idx_history_created ON optimization_history(created_at);
            CREATE INDEX IF NOT EXISTS idx_effectiveness_technique ON technique_effectiveness(technique_id);
            CREATE INDEX IF NOT EXISTS idx_effectiveness_defect ON technique_effectiveness(defect_id);
            CREATE INDEX IF NOT EXISTS idx_benchmark_strategy ON benchmark_results(strategy);
        """)

    logger.info(f"Database initialized at {DB_PATH}")


# ============================================================
# Optimization History
# ============================================================

def save_optimization(
    original_prompt: str,
    optimized_prompt: str,
    strategy: str,
    score_before: float,
    score_after: float,
    defects_before: List[Dict] = None,
    defects_after: List[Dict] = None,
    techniques_applied: List[Dict] = None,
    evolution_history: Dict = None,
    trajectory_history: Dict = None,
    critique_history: Dict = None,
    metadata: Dict = None,
    task_type: str = "general",
    domain: str = "general"
) -> int:
    """Save an optimization result to history. Returns the record ID."""
    improvement = round(score_after - score_before, 2)

    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO optimization_history
               (original_prompt, optimized_prompt, strategy, score_before, score_after,
                improvement, defects_before, defects_after, techniques_applied,
                evolution_history, trajectory_history, critique_history,
                metadata, task_type, domain)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                original_prompt,
                optimized_prompt,
                strategy,
                score_before,
                score_after,
                improvement,
                json.dumps(defects_before) if defects_before else None,
                json.dumps(defects_after) if defects_after else None,
                json.dumps(techniques_applied) if techniques_applied else None,
                json.dumps(evolution_history) if evolution_history else None,
                json.dumps(trajectory_history) if trajectory_history else None,
                json.dumps(critique_history) if critique_history else None,
                json.dumps(metadata) if metadata else None,
                task_type,
                domain
            )
        )
        record_id = cursor.lastrowid

    logger.info(f"Saved optimization #{record_id}: {strategy}, improvement={improvement}")
    return record_id


def get_history(
    limit: int = 20,
    offset: int = 0,
    strategy: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get optimization history, most recent first."""
    with get_connection() as conn:
        if strategy:
            rows = conn.execute(
                """SELECT * FROM optimization_history
                   WHERE strategy = ?
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (strategy, limit, offset)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM optimization_history
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (limit, offset)
            ).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_history_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific optimization record."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM optimization_history WHERE id = ?",
            (record_id,)
        ).fetchone()

    return _row_to_dict(row) if row else None


def get_history_stats() -> Dict[str, Any]:
    """Get aggregate statistics across all optimizations."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM optimization_history").fetchone()[0]

        if total == 0:
            return {
                "total_optimizations": 0,
                "by_strategy": {},
                "avg_improvement": 0.0,
                "best_improvement": 0.0
            }

        by_strategy = {}
        rows = conn.execute(
            """SELECT strategy, COUNT(*) as count, AVG(improvement) as avg_imp,
                      MAX(improvement) as max_imp, AVG(score_after) as avg_score
               FROM optimization_history GROUP BY strategy"""
        ).fetchall()
        for row in rows:
            by_strategy[row["strategy"]] = {
                "count": row["count"],
                "avg_improvement": round(row["avg_imp"], 2),
                "best_improvement": round(row["max_imp"], 2),
                "avg_final_score": round(row["avg_score"], 2)
            }

        overall = conn.execute(
            "SELECT AVG(improvement), MAX(improvement) FROM optimization_history"
        ).fetchone()

    return {
        "total_optimizations": total,
        "by_strategy": by_strategy,
        "avg_improvement": round(overall[0], 2),
        "best_improvement": round(overall[1], 2)
    }


# ============================================================
# Technique Effectiveness Learning
# ============================================================

def record_technique_result(
    technique_id: str,
    defect_id: str,
    improvement: float
):
    """Record the result of applying a technique to fix a defect."""
    success = 1 if improvement > 0 else 0

    with get_connection() as conn:
        # Upsert: insert or update
        existing = conn.execute(
            "SELECT * FROM technique_effectiveness WHERE technique_id = ? AND defect_id = ?",
            (technique_id, defect_id)
        ).fetchone()

        if existing:
            new_times = existing["times_applied"] + 1
            new_total = existing["total_improvement"] + improvement
            new_avg = round(new_total / new_times, 4)
            new_success = existing["success_count"] + success

            conn.execute(
                """UPDATE technique_effectiveness
                   SET times_applied = ?, total_improvement = ?, avg_improvement = ?,
                       success_count = ?, last_used = ?
                   WHERE technique_id = ? AND defect_id = ?""",
                (new_times, new_total, new_avg, new_success,
                 datetime.now().isoformat(), technique_id, defect_id)
            )
        else:
            conn.execute(
                """INSERT INTO technique_effectiveness
                   (technique_id, defect_id, times_applied, total_improvement,
                    avg_improvement, success_count, last_used)
                   VALUES (?, ?, 1, ?, ?, ?, ?)""",
                (technique_id, defect_id, improvement,
                 improvement, success, datetime.now().isoformat())
            )


def get_technique_effectiveness(
    technique_id: str,
    defect_id: str
) -> Optional[Dict[str, Any]]:
    """Get effectiveness data for a specific technique-defect pair."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM technique_effectiveness WHERE technique_id = ? AND defect_id = ?",
            (technique_id, defect_id)
        ).fetchone()

    return dict(row) if row else None


def get_top_techniques_for_defect(
    defect_id: str,
    limit: int = 5,
    min_applications: int = 3
) -> List[Dict[str, Any]]:
    """Get the most effective techniques for a given defect, based on learned data."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM technique_effectiveness
               WHERE defect_id = ? AND times_applied >= ?
               ORDER BY avg_improvement DESC LIMIT ?""",
            (defect_id, min_applications, limit)
        ).fetchall()

    return [dict(row) for row in rows]


def get_all_effectiveness() -> List[Dict[str, Any]]:
    """Get full technique effectiveness matrix for frontend heatmap."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT technique_id, defect_id, times_applied, avg_improvement, success_count
               FROM technique_effectiveness
               ORDER BY avg_improvement DESC"""
        ).fetchall()

    return [dict(row) for row in rows]


# ============================================================
# Benchmark Results
# ============================================================

def save_benchmark_result(
    benchmark_id: str,
    strategy: str,
    score_before: float,
    score_after: float,
    defects_fixed: int = 0,
    processing_time_ms: int = 0,
    cost: float = 0.0
) -> int:
    """Save a benchmark run result."""
    improvement = round(score_after - score_before, 2)

    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO benchmark_results
               (benchmark_id, strategy, score_before, score_after, improvement,
                defects_fixed, processing_time_ms, cost)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (benchmark_id, strategy, score_before, score_after, improvement,
             defects_fixed, processing_time_ms, cost)
        )
        return cursor.lastrowid


def get_benchmark_summary(strategy: Optional[str] = None) -> Dict[str, Any]:
    """Get aggregate benchmark results."""
    with get_connection() as conn:
        if strategy:
            rows = conn.execute(
                """SELECT strategy, COUNT(*) as count, AVG(improvement) as avg_imp,
                          AVG(score_after) as avg_score, AVG(processing_time_ms) as avg_time,
                          SUM(cost) as total_cost
                   FROM benchmark_results WHERE strategy = ? GROUP BY strategy""",
                (strategy,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT strategy, COUNT(*) as count, AVG(improvement) as avg_imp,
                          AVG(score_after) as avg_score, AVG(processing_time_ms) as avg_time,
                          SUM(cost) as total_cost
                   FROM benchmark_results GROUP BY strategy"""
            ).fetchall()

    results = {}
    for row in rows:
        results[row["strategy"]] = {
            "count": row["count"],
            "avg_improvement": round(row["avg_imp"], 2),
            "avg_final_score": round(row["avg_score"], 2),
            "avg_time_ms": round(row["avg_time"]) if row["avg_time"] else 0,
            "total_cost": round(row["total_cost"], 4) if row["total_cost"] else 0.0
        }

    return results


# ============================================================
# Helpers
# ============================================================

def _row_to_dict(row) -> Dict[str, Any]:
    """Convert a sqlite3.Row to a dict, parsing JSON fields."""
    d = dict(row)
    # Parse JSON fields
    for field in ["defects_before", "defects_after", "techniques_applied",
                  "evolution_history", "trajectory_history", "critique_history", "metadata"]:
        if d.get(field) and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except json.JSONDecodeError:
                pass
    return d


# ============================================================
# Initialize on import
# ============================================================

# Auto-initialize database when module is first imported
try:
    init_db()
except Exception as e:
    logger.warning(f"Could not initialize database: {e}")


# Singleton-style access
_db_initialized = True


def get_db_path() -> str:
    """Get the database file path"""
    return DB_PATH


__all__ = [
    "init_db",
    "get_connection",
    "save_optimization",
    "get_history",
    "get_history_by_id",
    "get_history_stats",
    "record_technique_result",
    "get_technique_effectiveness",
    "get_top_techniques_for_defect",
    "get_all_effectiveness",
    "save_benchmark_result",
    "get_benchmark_summary",
    "get_db_path"
]
