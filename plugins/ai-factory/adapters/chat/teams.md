# Microsoft Teams

**Status**: tested.

## Detect

The Microsoft 365 MCP connector is available (`teams_list_chats`, `chat_message_search`).

## Profile config

`{"channels": {"review": [{"name": "<chat title>", "chat_id": "<chat id from teams_list_chats>", "for": "<which tickets>"}]}, "me": "<user email>"}`

## Check

`teams_list_chats`, and confirm each `chat_id` is listed.

## Operations

- `post`: `teams_send_chat_message`, `bodyType: html`, one `<p>` per line, links in `<a href>`
  (in `text` mode Teams merges lines; outside `<a>` URLs are not clickable).
- `my_messages_today` / `find_links`: `chat_message_search` with `query: "https"`, `sender`, and
  `afterDateTime`; filter by `chatId`; read each hit with `read_resource` on its `uri`.

## Pitfalls

- `summary` in search results is truncated after two or three links: always read the full message.
- The search drops results and a page announced by `nextOffset` can come back empty: search again
  in windows of 6 hours at most and merge by message id.
- The connector cannot add reactions: "like" a message is a human task.
