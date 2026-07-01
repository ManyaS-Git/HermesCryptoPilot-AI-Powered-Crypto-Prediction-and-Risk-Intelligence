import aiosqlite
import logging
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DatabaseManager:
    def __init__(self, db_url: str = None):
        # Strip sqlite+aiosqlite:/// prefix for local file path
        if db_url is None:
            db_url = settings.DATABASE_URL

        self.db_path = db_url.replace("sqlite+aiosqlite:///", "")

    async def init_db(self):
        """Initializes the database schema."""
        logger.info(f"Initializing database at {self.db_path}")
        async with aiosqlite.connect(self.db_path) as db:
            # Predictions Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    timeframe TEXT,
                    raw_probability REAL,
                    calibrated_probability REAL,
                    predicted_move TEXT,
                    model_version TEXT
                )
            """)

            # Market Odds Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS market_odds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source TEXT NOT NULL,
                    implied_probability REAL,
                    odds REAL
                )
            """)

            # OHLCV Table (mostly for caching/backtesting)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ohlcv (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset TEXT NOT NULL,
                    timestamp DATETIME,
                    timeframe TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    UNIQUE(asset, timestamp, timeframe)
                )
            """)

            # Evaluation Metrics
            await db.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    asset TEXT,
                    brier_score REAL,
                    accuracy REAL,
                    sharpe_ratio REAL,
                    window_size INTEGER
                )
            """)

            # Position Recommendations (Signals)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS position_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    asset TEXT,
                    signal_direction TEXT,
                    kelly_size REAL,
                    fused_probability REAL,
                    expected_value REAL,
                    rationale TEXT
                )
            """)

            # Agent Runs (Telemetry/Audit)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS agent_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    agent_name TEXT,
                    status TEXT,
                    execution_time_ms REAL,
                    error_message TEXT
                )
            """)

            await db.commit()
            logger.info("Database schema initialized successfully.")

    async def execute_query(self, query: str, params: tuple = ()):
        """Executes a query and returns the results."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                await db.commit()
                return await cursor.fetchall()
