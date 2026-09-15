# Feature map

The feature map is the generated skill's coverage record. It lists the user-facing
features the project claims to have and, for each, the one method that proves it
works. A verification run is judged against this map. An unexecuted or methodless
row is a gap, not a pass.

## Contract

One table. Columns, in order:

| Column | Meaning | Rule |
|---|---|---|
| `feature` | A user-facing capability, named as the user knows it | Not an internal module name |
| `description` | What it does, in one line | Plain language |
| `verification_method` | The command or action that proves it works | Required. A feature with no method is a mapping gap, not a verified feature |
| `last_verified` | Date the method last passed | A date, or `never` |
| `status` | Coverage state | One of `verified`, `unverified`, `broken`, `removed` |

Status meanings:

- `verified`: a method exists and last passed at the date shown.
- `unverified`: a feature is listed but no method has run, or `last_verified` is
  `never`.
- `broken`: a method exists and the last run failed.
- `removed`: the feature no longer ships. Keep the row for history and mark it so.

A feature with a `verified` status but no `verification_method` is invalid. The
method is what the status rests on.

## Example

A feature map for a small web app plus a CLI. The example uses generic placeholders
only. A generated map replaces them with real commands from the project.

| feature | description | verification_method | last_verified | status |
|---|---|---|---|---|
| Sign in | A user logs in and reaches the dashboard | Drive the web UI: open the sign-in route, submit valid test credentials, assert the dashboard renders | 2026-09-15 | verified |
| Create item | A user adds a new record from the form | Drive the web UI: fill the create form, submit, assert the new row appears and the store holds one more item | never | unverified |
| Export report | A user exports the current list as CSV | Run the CLI: `app export --out /tmp/r.csv`, assert exit 0 and a non-empty CSV with the expected header | 2026-08-30 | broken |
| Delete item | A user removes a record | (method removed) | 2026-07-01 | removed |

The example carries four features with distinct verification methods: two driven
through the web UI, one through the CLI, and one retired. Only `Sign in` is
`verified`, because it has a method and a recent passing date. `Create item` is
`unverified` because it was never driven. `Export report` is `broken` because its
last CLI run failed. `Delete item` is `removed` and kept for history.
