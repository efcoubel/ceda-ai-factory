# Logs contract

| Operation | Input | Output |
|---|---|---|
| `errors_around` | service, environment, time, window | the errors and warnings in that window |
| `errors_since` | service, environment, since | grouped errors with counts, for a log watch |

Production logs may be read (they are not data writes); they are quoted with business identifiers
only.
