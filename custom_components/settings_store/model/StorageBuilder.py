from pathlib import Path

from ..utils.Database import Database


class StorageBuilder:
    def __init__(self, hass, storagePath):
        self._hass = hass
        self._storagePath = Path(storagePath)

    async def async_build(self):
        await self._hass.async_add_executor_job(self._build)

    async def async_remove(self):
        await self._hass.async_add_executor_job(self._remove)

    def _build(self):
        self._storagePath.parent.mkdir(parents=True, exist_ok=True)

        with Database.connect(self._storagePath) as connection:
            connection.execute('''
                CREATE TABLE IF NOT EXISTS settings_store (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scope TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value TEXT NOT NULL,
                    UNIQUE(scope, name)
                )
            ''')

    def _remove(self):
        self._storagePath.unlink(missing_ok=True)
        Path(f"{self._storagePath}-wal").unlink(missing_ok=True)
        Path(f"{self._storagePath}-shm").unlink(missing_ok=True)
        Path(f"{self._storagePath}-journal").unlink(missing_ok=True)
