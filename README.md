# Settings Store

This Home Assistant integration provides persistent, key-value storage backed by SQLite for automations, scripts, and
integrations.

It allows you to store, update, retrieve, and delete arbitrary settings organized by **scopes** (namespaces) and
**keys**, persisting them safely across Home Assistant restarts.

It is especially useful when you want to:

- Avoid cluttering Home Assistant with dummy helper entities (`input_text`, `input_number`, `input_boolean`, template
  sensors, or switches) created solely to persist intermediate states or automation variables.
- Store state, runtime configuration, or counters that need to persist across restarts.
- Organize settings into logical namespaces (`scope`) and key names (`name`).
- Share custom configuration data between different automations, scripts, and templates.
- Dynamically update and query parameters at runtime without modifying YAML configuration files.

## Installation

This integration is installed via **HACS**:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=catgiggle&repository=HomeAssistant-SettingsStore)

1. Click the button above to open the repository in HACS.
2. Click **Download** to download the integration.
3. Restart Home Assistant.

**Note:** Alternatively, you can add `https://github.com/catgiggle/HomeAssistant-SettingsStore` as a custom repository
under **HACS → Integrations**.

## Configuration

[![Open your Home Assistant instance and show an integration.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=settings_store)

1. Click the button above or go to **Settings → Devices & Services → Add Integration** and search for **Settings
   Store**.
2. Configure the instance parameters:

You can add **multiple instances** of this integration. Each instance represents an isolated SQLite settings store.

![installation.png](docs/images/installation.png)

| Parameter       | Description                                                                                                               |
|-----------------|---------------------------------------------------------------------------------------------------------------------------|
| `Display name`  | Display name for the instance (shown in Home Assistant UI).                                                               |
| `Internal name` | Unique identifier used as the SQLite database filename. If left empty, it is generated automatically from `Display name`. |

## Features

- Persistent key-value storage backed by SQLite (`.storage/settings_store/<name>.db`)
- Grouping of settings using scopes (namespaces) and keys
- Automatic tracking of creation (`created_at`) and modification (`modified_at`) timestamps for each entry
- No need to create throwaway helper entities (`input_*`, dummy switches/sensors) just to store state
- Atomic upsert operations (insert or update on key conflict)
- Diagnostic sensor reporting total stored entries count
- Response data support in `get` and `list` services for direct use in automations, scripts, and templates
- Ability to delete individual entries or clear the entire store
- Isolated storage per configured instance

![features.png](docs/images/features.png)

## Entities

Each configured instance creates the following diagnostic sensor:

- `Entries`: Displays the current total number of entries stored
  in the instance's database. This sensor automatically updates whenever records are created, updated, deleted or
  cleared. Its `entity_id` is passed as a target parameter to the integration's services.
  - Attributes:
    - `latest_store_changed_at`: Timestamp of the most recent change to the store (create, update, delete or clear) (`YYYY-MM-DD HH:MM:SS` or `null`).
    - `latest_entry_created_at`: Timestamp of the most recently created entry (`YYYY-MM-DD HH:MM:SS` or `null`).
    - `latest_entry_modified_at`: Timestamp of the most recently modified entry (`YYYY-MM-DD HH:MM:SS` or `null`).

## Services

This integration provides the following services:

### `settings_store.set`

Sets or updates a value for a specific scope and name in the store. If the entry already exists, its value is updated.

| Field       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| `entity_id` | Entity ID of the Settings Store sensor (identifies target storage instance) |
| `scope`     | Scope / namespace for grouping settings (optional, defaults to `default`)   |
| `name`      | Setting key name                                                            |
| `value`     | Value to store                                                              |

### `settings_store.get`

Retrieves the stored value and timestamps for a given scope and name. Supports returning service response data.

| Field       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| `entity_id` | Entity ID of the Settings Store sensor (identifies target storage instance) |
| `scope`     | Scope / namespace identifier (optional, defaults to `default`)              |
| `name`      | Setting key name                                                            |

#### Response

Returns a dictionary containing the stored value and timestamps:

```json
{
  "value": "15",
  "created_at": "2026-10-12 14:00:00",
  "modified_at": "2026-10-12 14:30:00"
}
```

- `value`: Stored value string or `null` if the key does not exist.
- `created_at`: Creation timestamp formatted as `YYYY-MM-DD HH:MM:SS` (or `null` if not found).
- `modified_at`: Last modification timestamp formatted as `YYYY-MM-DD HH:MM:SS` (or `null` if not found).

### `settings_store.list`

Retrieves all stored entries for a given scope, ordered alphabetically by key name. Supports returning service response data.

| Field       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| `entity_id` | Entity ID of the Settings Store sensor (identifies target storage instance) |
| `scope`     | Scope / namespace identifier (optional, defaults to `default`)              |

#### Response

Returns a dictionary containing a `list` array of stored entries:

```json
{
  "list": [
    {
      "name": "interval_minutes",
      "value": "30",
      "created_at": "2026-10-12 10:00:00",
      "modified_at": "2026-10-12 10:00:00"
    },
    {
      "name": "last_run_duration",
      "value": "15",
      "created_at": "2026-10-12 14:00:00",
      "modified_at": "2026-10-12 14:30:00"
    }
  ]
}
```

- `list`: Array of entries for the requested scope (ordered alphabetically by `name`).
  - `name`: Setting key name.
  - `value`: Stored value string.
  - `created_at`: Creation timestamp formatted as `YYYY-MM-DD HH:MM:SS`.
  - `modified_at`: Last modification timestamp formatted as `YYYY-MM-DD HH:MM:SS`.

### `settings_store.delete`

Deletes a specific setting identified by scope and name.

| Field       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| `entity_id` | Entity ID of the Settings Store sensor (identifies target storage instance) |
| `scope`     | Scope / namespace identifier (optional, defaults to `default`)              |
| `name`      | Setting key name                                                            |

### `settings_store.clear`

Removes all stored entries from the instance's database.

| Field       | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| `entity_id` | Entity ID of the Settings Store sensor (identifies target storage instance) |

## Usage Examples

### Storing a Value

```yaml
action: settings_store.set
data:
  entity_id: sensor.settings_store_main_entries
  scope: irrigation
  name: last_run_duration
  value: "15"
```

### Retrieving a Value in an Automation or Script

```yaml
action: settings_store.get
data:
  entity_id: sensor.settings_store_main_entries
  scope: irrigation
  name: last_run_duration
response_variable: saved_setting

action: notify.persistent_notification
data:
  message: "Last duration was {{ saved_setting.value }} minutes (modified at {{ saved_setting.modified_at }})."
```

### Listing Entries in an Automation or Script

```yaml
action: settings_store.list
data:
  entity_id: sensor.settings_store_main_entries
  scope: irrigation
response_variable: irrigation_settings

action: notify.persistent_notification
data:
  message: >
    {% for entry in irrigation_settings.list %}
      {{ entry.name }}: {{ entry.value }} (created: {{ entry.created_at }}, modified: {{ entry.modified_at }})
    {% endfor %}
```

### Deleting a Setting

```yaml
action: settings_store.delete
data:
  entity_id: sensor.settings_store_main_entries
  scope: irrigation
  name: last_run_duration
```

### Clearing All Settings

```yaml
action: settings_store.clear
data:
  entity_id: sensor.settings_store_main_entries
```

## Notes

- Settings are stored in `.storage/settings_store/<name>.db` within your Home Assistant configuration directory.
- Values are stored as strings in SQLite, allowing you to store primitive values, JSON strings, or serialized payloads.
- Removing an instance through the Home Assistant UI will automatically delete its associated database file.
