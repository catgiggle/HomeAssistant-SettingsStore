import sqlite3
from pathlib import Path


class StorageBuilder:
    def __init__(self, database):
        self._database = Path(database)

    def build(self):
        self._database.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self._database) as connection:
            connection.execute('''
                CREATE TABLE IF NOT EXISTS settings_store (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scope TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value TEXT NOT NULL,
                    UNIQUE(scope, name)
                )
            ''')

    def remove(self):
        self._database.unlink(missing_ok=True)
        Path(f"{self._database}-wal").unlink(missing_ok=True)
        Path(f"{self._database}-shm").unlink(missing_ok=True)
        Path(f"{self._database}-journal").unlink(missing_ok=True)
