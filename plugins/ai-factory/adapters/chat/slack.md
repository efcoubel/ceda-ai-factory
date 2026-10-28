# Slack

**Status**: draft.

## Detect

A Slack MCP connector is available. Ask for the channel used for code review.

## Profile config

`{"channels": {"review": [{"name": "#code-review", "id": "<C…>"}]}, "me": "<member id>"}`

## Check

Read the last message of each channel.

## Operations

- `post`: post to the channel id; links in Slack `<url|text>` format.
- `my_messages_today` / `find_links`: channel history since 00:00 local time, filtered on the author.
