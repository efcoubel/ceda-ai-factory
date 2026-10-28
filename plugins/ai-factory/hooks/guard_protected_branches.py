#!/usr/bin/env python3
"""PreToolUse hook (Bash): nothing reaches a protected branch, by merge or push, without the user.

Protected branches come from the ai-factory profile of the project the command runs in. Outside an
ai-factory project the hook does nothing.
"""
import json
import os
import re
import shlex
import subprocess
import sys

PUSH_OPTIONS_WITH_VALUE = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
GIT_OPTIONS_WITH_VALUE = {"-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
MERGE_CLI_OPTIONS_WITH_VALUE = {"-m", "--message", "--squash-message", "--sha", "-R", "--repo", "-b", "--body", "-t", "--subject"}
SEPARATORS = {"&&", "||", ";", "|", "&", "(", ")"}


def tokenize(command):
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return re.sub(r"(&&|\|\||[;|&()])", r" \1 ", command).split()


def find_profile(directory):
    current = os.path.realpath(directory)
    while True:
        candidate = os.path.join(current, ".ai-factory", "profile.json")
        if os.path.isfile(candidate):
            return current, candidate
        parent = os.path.dirname(current)
        if parent == current:
            return None, None
        current = parent


def protected_branches(directory):
    root, profile_path = find_profile(directory)
    if not profile_path:
        return None
    try:
        with open(profile_path, encoding="utf-8") as handle:
            profile = json.load(handle)
    except (OSError, ValueError):
        # An unreadable profile protects the usual production branches rather than nothing.
        return {"main", "master", "prod", "production"}
    branches = set()
    for repo in profile.get("repos", []):
        branches.update(branch.lower() for branch in repo.get("protected_branches", []))
    return branches


def current_branch(directory):
    try:
        return subprocess.run(
            ["git", "-C", directory, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def is_protected(branch, protected):
    return branch.removeprefix("refs/heads/").lower() in protected


def read_json(directory, command):
    try:
        output = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=8).stdout
        return json.loads(output)
    except (OSError, subprocess.SubprocessError, ValueError):
        return {}


def arguments(tokens, start):
    end = start
    while end < len(tokens) and tokens[end] not in SEPARATORS:
        end += 1
    return tokens[start:end]


def selectors(args, start):
    found, index = [], start
    while index < len(args):
        if args[index] in ("-R", "--repo") and index + 1 < len(args):
            found += [args[index], args[index + 1]]
            index += 2
        elif args[index] in MERGE_CLI_OPTIONS_WITH_VALUE:
            index += 2
        elif args[index].startswith("-"):
            index += 1
        else:
            found.insert(0, args[index])
            index += 1
    return found


def git_reason(args, directory, protected):
    index = 0
    while index < len(args) and args[index].startswith("-"):
        if args[index] == "-C" and index + 1 < len(args):
            directory = os.path.join(directory, os.path.expanduser(args[index + 1]))
            index += 2
        elif args[index] in GIT_OPTIONS_WITH_VALUE:
            index += 2
        else:
            index += 1
    if index >= len(args):
        return None
    subcommand, rest = args[index], args[index + 1:]

    if subcommand == "merge":
        if any(option in rest for option in ("--abort", "--quit")):
            return None
        branch = current_branch(directory)
        return f"`git merge` into `{branch}`" if is_protected(branch, protected) else None

    if subcommand == "push":
        if "--all" in rest or "--mirror" in rest:
            return "`git push --all/--mirror` would push protected branches"
        positional, position = [], 0
        while position < len(rest):
            if rest[position] in PUSH_OPTIONS_WITH_VALUE:
                position += 2
            elif rest[position].startswith("-"):
                position += 1
            else:
                positional.append(rest[position])
                position += 1
        targets = [ref.split(":")[-1].lstrip("+") for ref in positional[1:]]
        if not targets or "HEAD" in targets:
            targets.append(current_branch(directory))
        for target in targets:
            if is_protected(target, protected):
                return f"push to `{target}`"
    return None


def glab_reason(args, directory, protected):
    if args[:2] == ["mr", "merge"]:
        target = read_json(directory, ["glab", "mr", "view", *selectors(args, 2), "--output", "json"]).get("target_branch", "")
        if not target:
            return "`glab mr merge` to an unknown target branch (a protected branch is not excluded)"
        return f"`glab mr merge` into `{target}`" if is_protected(target, protected) else None
    if args[:1] == ["api"]:
        for argument in args:
            match = re.search(r"(projects/[^/]+/merge_requests/\d+)/merge\b", argument)
            if match:
                target = read_json(directory, ["glab", "api", match.group(1)]).get("target_branch", "")
                if not target or is_protected(target, protected):
                    return f"merging a merge request into `{target or 'an unknown branch'}` through the GitLab API"
    return None


def gh_reason(args, directory, protected):
    if args[:2] == ["pr", "merge"]:
        target = read_json(directory, ["gh", "pr", "view", *selectors(args, 2), "--json", "baseRefName"]).get("baseRefName", "")
        if not target:
            return "`gh pr merge` to an unknown base branch (a protected branch is not excluded)"
        return f"`gh pr merge` into `{target}`" if is_protected(target, protected) else None
    if args[:1] == ["api"] and any(re.search(r"pulls/\d+/merge\b", argument) for argument in args):
        return "merging a pull request through the GitHub API"
    return None


def block_reason(command, directory):
    protected = protected_branches(directory)
    if not protected:
        return None
    tokens = tokenize(command)
    for index, token in enumerate(tokens):
        name = os.path.basename(token)
        if name == "cd" and index + 1 < len(tokens):
            directory = os.path.join(directory, os.path.expanduser(tokens[index + 1]))
        elif name == "git":
            reason = git_reason(arguments(tokens, index + 1), directory, protected)
        elif name == "glab":
            reason = glab_reason(arguments(tokens, index + 1), directory, protected)
        elif name == "gh":
            reason = gh_reason(arguments(tokens, index + 1), directory, protected)
        else:
            continue
        if name != "cd" and reason:
            return reason
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
                    f"Blocked by ai-factory: {reason}. Protected branches (see .ai-factory/profile.json) "
                    "are merged and pushed by the user only. Give the user the command to run instead "
                    "of looking for a workaround."
                ),
            }
        }))


if __name__ == "__main__":
    main()
