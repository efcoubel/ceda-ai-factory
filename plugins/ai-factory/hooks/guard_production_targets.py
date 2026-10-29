#!/usr/bin/env python3
"""PreToolUse hook (Bash): no deploy, write or data command reaches a production target.

Production targets come from the ai-factory profile of the project the command runs in:
`production_targets`, the database projects of `production_environments`, and the `.firebaserc`
aliases pointing to them. Outside an ai-factory project the hook does nothing.
"""
import json
import os
import re
import sys

from guard_protected_branches import SEPARATORS, arguments, find_profile, tokenize

TOOLS = {
    "firebase", "gcloud", "gsutil", "bq", "kubectl", "helm", "fly", "flyctl", "vercel", "netlify",
    "heroku", "aws", "az", "terraform", "supabase", "railway", "wrangler",
}
READ_VERBS = {
    "list", "ls", "describe", "get", "read", "log", "logs", "functions:log", "tail", "view", "show",
    "status", "plan", "projects:list", "--help", "help",
}
FIREBASE_WRITES = ("deploy", "hosting:", "functions:delete", "functions:config:set", "firestore:delete",
                   "database:set", "database:push", "database:update", "database:remove",
                   "remoteconfig:", "auth:import", "ext:install", "ext:update")


def string_values(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [item for nested in value.values() for item in string_values(nested)]
    if isinstance(value, list):
        return [item for nested in value for item in string_values(nested)]
    return []


def production_targets(directory):
    root, profile_path = find_profile(directory)
    if not profile_path:
        return None
    try:
        with open(profile_path, encoding="utf-8") as handle:
            profile = json.load(handle)
    except (OSError, ValueError):
        return None
    targets = set(string_values(profile.get("production_targets", [])))
    database = profile.get("tools", {}).get("database", {}).get("config", {})
    environments = set(database.get("production_environments", ["production"]))
    for key in ("projects", "sections", "services"):
        for name, value in (database.get(key) or {}).items():
            if name in environments:
                targets.update(string_values(value))
            elif isinstance(value, dict):
                targets.update(string_values({env: v for env, v in value.items() if env in environments}))
    targets.discard("emulator")
    paths = [root] + [os.path.join(root, repo.get("path", ".")) for repo in profile.get("repos", [])]
    for path in paths:
        try:
            with open(os.path.join(path, ".firebaserc"), encoding="utf-8") as handle:
                aliases = json.load(handle).get("projects", {})
        except (OSError, ValueError):
            continue
        for alias, project in aliases.items():
            if project in targets or alias in environments:
                targets.update({alias, project})
    return {target for target in targets if target}


def names_target(token, targets):
    return any(re.search(rf"(?<![\w-]){re.escape(target)}(?![\w-])", token) for target in targets)


def firebase_without_project(args):
    if any(arg in ("--project", "-P") or arg.startswith("--project=") for arg in args):
        return False
    return any(arg.startswith(FIREBASE_WRITES) for arg in args if not arg.startswith("-"))


def block_reason(command, directory):
    targets = production_targets(directory)
    if not targets:
        return None
    tokens = tokenize(command)
    for index, token in enumerate(tokens):
        name = os.path.basename(token)
        if name == "cd" and index + 1 < len(tokens):
            directory = os.path.join(directory, os.path.expanduser(tokens[index + 1]))
            continue
        if name not in TOOLS:
            continue
        args = arguments(tokens, index + 1)
        start = index
        while start > 0 and tokens[start - 1] not in SEPARATORS:
            start -= 1
        assignments = [t for t in tokens[start:index] if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t)]
        if any(arg in READ_VERBS for arg in args):
            continue
        if any(names_target(arg, targets) for arg in args + assignments):
            return f"`{name}` on a production target"
        if name == "firebase" and firebase_without_project(args):
            return "`firebase` writing to the active project without `--project` (it may be production)"
    return None


def main():
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")
    reason = block_reason(command, data.get("cwd") or os.getcwd())
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Blocked by ai-factory: {reason}. Production (see .ai-factory/profile.json) is "
                    "deployed to and written by the user only. Name a non-production project, or give "
                    "the user the command to run instead of looking for a workaround."
                ),
            }
        }))


if __name__ == "__main__":
    main()
