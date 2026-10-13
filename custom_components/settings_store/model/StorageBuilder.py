from datetime import datetime
from pathlib import Path

from ..constants import *
from ..utils.Database import Database
from ..utils.Migration import Migration


class StorageBuilder:
    def __init__(self, hass, storagePath):
        self._hass = hass
        self._storagePath = Path(storagePath)
        self._migration = Migration(DOMAIN)

    async def async_build(self):
        await self._hass.async_add_executor_job(self._build)

    async def async_remove(self):
        await self._hass.async_add_executor_job(self._remove)

    def _build(self):
        self._storagePath.parent.mkdir(parents=True, exist_ok=True)

        with Database.connect(self._storagePath) as connection:
            self._migration.execute(connection, [
                self._migrate_2026_09_10_10_23_59,
                self._migrate_2026_10_12_14_38_31,
            ])

    def _remove(self):
        self._storagePath.unlink(missing_ok=True)
        Path(f"{self._storagePath}-wal").unlink(missing_ok=True)
        Path(f"{self._storagePath}-shm").unlink(missing_ok=True)
        Path(f"{self._storagePath}-journal").unlink(missing_ok=True)

    @staticmethod
    def _migrate_2026_09_10_10_23_59(connection):
        connection.execute('''
            CREATE TABLE IF NOT EXISTS settings_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT NOT NULL,
                name TEXT NOT NULL,
                value TEXT NOT NULL,
                UNIQUE(scope, name)
            )
        ''')

    @staticmethod
    def _migrate_2026_10_12_14_38_31(connection):
        now = datetime.now().strftime(DATETIME_FORMAT)

        connection.execute('''
            ALTER TABLE settings_store RENAME TO settings_store_old
        ''')
        connection.execute('''
            CREATE TABLE settings_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT NOT NULL,
                name TEXT NOT NULL,
                value TEXT NOT NULL,
                createdAt DATETIME NOT NULL,
                modifiedAt DATETIME NOT NULL,
                UNIQUE(scope, name)
            )
        ''')
        connection.execute('''
            INSERT INTO settings_store (id, scope, name, value, createdAt, modifiedAt)
            SELECT id, scope, name, value, ?, ?
            FROM settings_store_old
        ''', (now, now))
        connection.execute('''
            DROP TABLE settings_store_old
        ''')
