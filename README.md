# Settings Store

This Home Assistant integration provides persistent, key-value storage backed by SQLite for automations, scripts, and
integrations.

It allows you to store, update, retrieve, and delete arbitrary settings organized by **scopes** (namespaces) and **keys**, persisting them safely across Home Assistant restarts.

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
- Diagnostic sensor reporting total stored entries count along with store-wide and per-scope timestamps
- Response data support in `get`, `list`, and `all` services for direct use in automations, scripts, and templates
- Ability to delete individual entries or clear the entire store
- Isolated storage per configured instance

![features.png](docs/images/features.png)

## Entities

Each configured instance creates the following diagnostic sensor:

- `Entries`: Displays the current total number of entries stored
  in the instance's database. This sensor automatically updates whenever records are created, updated, deleted or
  cleared. Its `entity_id` is passed in the `store` parameter to the integration's services.
    - Attributes:
        - `store_created_at`: Timestamp of the first entry created in the store (`YYYY-MM-DD HH:MM:SS` or `null`).
        - `store_modified_at`: Timestamp of the most recently modified entry across the entire store (`YYYY-MM-DD HH:MM:SS` or `null`).
        - `<scope>_created_at`: Timestamp of the first entry created in a given scope (`YYYY-MM-DD HH:MM:SS`).
        - `<scope>_modified_at`: Timestamp of the most recently modified entry for a given scope (`YYYY-MM-DD HH:MM:SS`).

## Services

This integration provides the following services:

### `settings_store.set`

Sets or updates a value for a specific scope and name in the store. If the entry already exists, its value is updated.
Alternatively, provide `id` to update an existing entry. An unknown `id` does not create an entry.
Updating by `id` changes the value and modification timestamp; the entry's name and scope remain unchanged.

| Field   | Description                                                                   |
|---------|-------------------------------------------------------------------------------|
| `store` | Entity ID of the Settings Store sensor (identifies target storage instance)   |
| `id`    | Optional ID of the entry to update; cannot be combined with `scope` or `name` |
| `scope` | Scope (defaults to `default` when updating by name)                           |
| `name`  | Setting key name (required without `id`)                                      |
| `value` | Value to store                                                                |

### `settings_store.get`

Retrieves the stored value and timestamps by `id` or by scope and name. Supports returning service response data.

| Field   | Description                                                                 |
|---------|-----------------------------------------------------------------------------|
| `store` | Entity ID of the Settings Store sensor (identifies target storage instance) |
| `id`    | Optional entry ID; cannot be combined with `scope` or `name`                |
| `scope` | Scope (defaults to `default` when retrieving by name)                       |
| `name`  | Setting key name (required without `id`)                                    |

#### Response

Returns a dictionary containing the entry ID, stored value and timestamps:

```json
{
  "id": 1,
  "value": "15",
  "created_at": "2026-10-12 14:00:00",
  "modified_at": "2026-10-12 14:30:00"
}
```

- `id`: Entry ID or `null` if the key does not exist.
- `value`: Stored value string or `null` if the key does not exist.
- `created_at`: Creation timestamp formatted as `YYYY-MM-DD HH:MM:SS` (or `null` if not found).
- `modified_at`: Last modification timestamp formatted as `YYYY-MM-DD HH:MM:SS` (or `null` if not found).

### `settings_store.list`

Retrieves all stored entries for a given scope, ordered alphabetically by key name. Supports returning service response data.

| Field   | Description                                                                 |
|---------|-----------------------------------------------------------------------------|
| `store` | Entity ID of the Settings Store sensor (identifies target storage instance) |
| `scope` | Scope / namespace identifier (optional, defaults to `default`)              |

#### Response

Returns a dictionary containing a `list` array of stored entries:

```json
{
  "list": [
    {
      "id": 1,
      "name": "interval_minutes",
      "value": "30",
      "created_at": "2026-10-12 10:00:00",
      "modified_at": "2026-10-12 10:00:00"
    },
    {
      "id": 2,
      "name": "last_run_duration",
      "value": "15",
      "created_at": "2026-10-12 14:00:00",
      "modified_at": "2026-10-12 14:30:00"
    }
  ]
}
```

- `list`: Array of entries for the requested scope (ordered alphabetically by `name`).
    - `id`: Entry ID.
    - `name`: Setting key name.
    - `value`: Stored value string.
    - `created_at`: Creation timestamp formatted as `YYYY-MM-DD HH:MM:SS`.
    - `modified_at`: Last modification timestamp formatted as `YYYY-MM-DD HH:MM:SS`.

### `settings_store.all`

Retrieves all stored entries across all scopes, ordered alphabetically by scope and key name. Supports returning service response data.

| Field   | Description                                                                 |
|---------|-----------------------------------------------------------------------------|
| `store` | Entity ID of the Settings Store sensor (identifies target storage instance) |

#### Response

Returns a dictionary containing a `list` array of stored entries:

```json
{
  "list": [
    {
      "id": 3,
      "name": "threshold",
      "scope": "climate",
      "value": "22",
      "created_at": "2026-10-13 08:00:00",
      "modified_at": "2026-10-13 08:00:00"
    },
    {
      "id": 2,
      "name": "last_run_duration",
      "scope": "irrigation",
      "value": "15",
      "created_at": "2026-10-12 14:00:00",
      "modified_at": "2026-10-12 14:30:00"
    }
  ]
}
```

- `list`: Array of all entries across all scopes (ordered alphabetically by `scope`, then by `name`).
    - `id`: Entry ID.
    - `scope`: Scope / namespace identifier.
    - `name`: Setting key name.
    - `value`: Stored value string.
    - `created_at`: Creation timestamp formatted as `YYYY-MM-DD HH:MM:SS`.
    - `modified_at`: Last modification timestamp formatted as `YYYY-MM-DD HH:MM:SS`.

### `settings_store.delete`

Deletes a specific setting identified by ID or by scope and name. An unknown ID has no effect.

| Field   | Description                                                                 |
|---------|-----------------------------------------------------------------------------|
| `store` | Entity ID of the Settings Store sensor (identifies target storage instance) |
| `id`    | Optional entry ID; cannot be combined with `scope` or `name`                |
| `scope` | Scope / namespace identifier (optional, defaults to `default` without `id`) |
| `name`  | Setting key name (required without `id`)                                    |

### `settings_store.clear`

Removes all stored entries from the instance's database.

| Field   | Description                                                                 |
|---------|-----------------------------------------------------------------------------|
| `store` | Entity ID of the Settings Store sensor (identifies target storage instance) |

## Usage Examples

### Storing a Value

```yaml
action: settings_store.set
data:
  store: sensor.settings_store_main_entries
  scope: irrigation
  name: last_run_duration
  value: "15"
```

### Retrieving a Value in an Automation or Script

```yaml
action: settings_store.get
data:
  store: sensor.settings_store_main_entries
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
  store: sensor.settings_store_main_entries
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
  store: sensor.settings_store_main_entries
  scope: irrigation
  name: last_run_duration
```

To update or delete an entry by ID, provide `id` instead of `name` and `scope`:

```yaml
action: settings_store.set
data:
  store: sensor.settings_store_main_entries
  id: 2
  value: "20"
```

```yaml
action: settings_store.delete
data:
  store: sensor.settings_store_main_entries
  id: 2
```

### Retrieving All Entries Across Scopes

```yaml
action: settings_store.all
data:
  store: sensor.settings_store_main_entries
response_variable: all_settings

action: notify.persistent_notification
data:
  message: >
    {% for entry in all_settings.list %}
      [{{ entry.scope }}] {{ entry.name }}: {{ entry.value }} (modified: {{ entry.modified_at }})
    {% endfor %}
```

### Clearing All Settings

```yaml
action: settings_store.clear
data:
  store: sensor.settings_store_main_entries
```

## Notes

- Settings are stored in `.storage/settings_store/<name>.db` within your Home Assistant configuration directory.
- Values are stored as strings in SQLite, allowing you to store primitive values, JSON strings, or serialized payloads.
- Removing an instance through the Home Assistant UI will automatically delete its associated database file.
