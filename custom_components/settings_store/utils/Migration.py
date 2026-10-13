class Migration:
    def __init__(self, name):
        self._name = name

    def execute(self, connection, migrations):
        self._prepare(connection)

        currentVersion = self._getVersion(connection)

        for version, migration in enumerate(migrations[currentVersion:], start=currentVersion + 1):
            migration(connection)
            self._setVersion(connection, version)

    @staticmethod
    def _prepare(connection):
        connection.execute('''
            CREATE TABLE IF NOT EXISTS migration_version (
                name TEXT PRIMARY KEY,
                version INTEGER NOT NULL
            )
        ''')

    def _getVersion(self, connection):
        row = connection.execute(
            'SELECT version FROM migration_version WHERE name = ?',
            (self._name,)
        ).fetchone()

        return int(row[0]) if row else 0

    def _setVersion(self, connection, version):
        connection.execute('''
            INSERT INTO migration_version (name, version)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET
                version = excluded.version
        ''', (self._name, version))
