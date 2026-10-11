# Unit tests

Run from the repository root with the existing Python 3.14 virtual environment:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The suite uses standard-library `unittest` and the application's existing PySide6
dependency. It needs no database, credentials, network connection, or GUI window.
It covers every class in `Data`, including enums, the grouping protocol, and the
custom exception. Parameterized subtests cover enum values, skill mappings,
required fields, malformed inputs, defaults, serialization, and nested models.

The models currently do not enforce field annotations or numeric bounds at
runtime. Tests document this behavior rather than inventing validation rules.
Invalid enum values, missing dictionary keys, malformed containers, and invalid
skill names are tested for their existing exceptions.

Eight regression tests use `expectedFailure` to expose existing implementation
defects without changing application code:

- Weapon deserialization omits required `group` and `is_melee` arguments.
- Weapon dictionary serialization omits those two fields.
- The range factory rejects the serialized `MeleeRange` discriminator.
- Melee range deserialization expects a different strength multiplier key.
- NPC's default skills factory calls `Skills` without its required argument.
- NPC's default skill pool tries to read a nonexistent `none` attribute.
- NPC deserialization with a nested weapon fails through weapon deserialization.
- NPC JSON uses different armor name and shock keys from its deserializer.

Fixing any of these should produce an unexpected success; remove the associated
`expectedFailure` decorator when fixing the implementation. Expected failures
are reported separately from passing tests and do not mean these behaviors work.

## DatabaseManagement tests

`test_database_management.py` covers `NpcDB`, `WeaponDB`, `NotionClient`,
`Text`, `Annotations`, `RichText`, `TitleProperty`, and `RichTextProperty`.
Each test has a comment describing its assertions. Run just these tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_database_management -v
```

Repository tests replace their `NotionClient` constructors with autospecced mocks.
Client tests replace `requests.post`, `requests.get`, and `requests.patch`, and
use a fake token. Every database test also blocks `requests.sessions.Session.request`
so a missed HTTP mock raises an assertion instead of contacting Notion. No real
database or credentials are used, and no production changes are needed for mocking.

Coverage includes CRUD request payloads, pagination, empty responses, malformed
stored JSON, missing properties, invalid model inputs, transport errors, timeouts,
API error responses, and property serialization. Inputs that currently have no
local validation are explicitly documented as being forwarded or accepted.

Three additional expected failures record existing defects: weapon retrieval
fails through `Weapon.from_dict`, rich text serialization leaves `plain_text`
empty because the constructor sets `plainText`, and an absent `href` is serialized
as the string `"null"` instead of JSON null. NPC picture methods are placeholders;
their test documents that they currently do nothing and make no database calls.

## Windows tests

`test_windows.py` covers every class in `Windows` and `Windows/NPCTab`.
`TabWindowBar.py` is empty and has no classes to test. Every test includes a
comment explaining what it verifies. Run these tests from the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_windows -v
```

The tests create a shared Qt application with `QT_QPA_PLATFORM=offscreen` and
dispose of test widgets and deferred deletions. No visible GUI is opened.
`NpcTab` tests mock `NpcDB` and replace the shared example NPCs with fresh
fixtures to avoid modifying application example data. HTTP requests are blocked
in widget tests as an additional safeguard against real database calls.

Coverage includes grouping, filtering, selection and removal signals, titles,
attribute updates and numeric bounds, edit controls, skill and weapon text,
picture scaling, and detail view replacement. Placeholder add/edit methods are
tested for their current behavior without asserting that editors exist.

Three expected failures record existing UI defects: `all_children_hidden`
returns the opposite of its name, selecting a size stores an integer instead of
the size string, and canceling edits does not restore the original NPC model.
Application code is unchanged.
