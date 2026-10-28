# Grafana / Loki

**Status**: draft.

## Detect

A Grafana URL in the docs or env files; a Grafana MCP server, or a service account token reference.

## Profile config

`{"url": "https://<grafana host>", "org_id": 1, "datasource": "<loki uid>", "token_ref": "env:GRAFANA_TOKEN", "service_label": "service_name", "services": {"<repo>": {"production": "<label value>"}}}`

## Check

One Loki query for the last 5 minutes on one service.

## Operations

- `errors_around`: LogQL `{<service_label>="<value>"} |= "" | level=~"error|critical"` over the window.
- `errors_since`: the same with `count_over_time` grouped by message pattern.
