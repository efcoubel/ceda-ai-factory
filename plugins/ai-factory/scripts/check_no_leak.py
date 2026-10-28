"""Fails if the plugin mentions a term from a private project.

Terms come from `.leak-terms` at the repository root (one per line, git-ignored), so the list of
private names is never published itself. Run before every release: python3 -I scripts/check_no_leak.py
"""
import os
import re
import sys

PLUGIN = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
REPOSITORY = os.path.dirname(os.path.dirname(PLUGIN))
TERMS_FILE = os.path.join(REPOSITORY, ".leak-terms")


def terms() -> list[str]:
    if not os.path.isfile(TERMS_FILE):
        sys.exit(f"Missing {TERMS_FILE}: list the private terms to keep out of the plugin, one per line.")
    with open(TERMS_FILE, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip() and not line.startswith("#")]


def main() -> int:
    pattern = re.compile("|".join(re.escape(term) for term in terms()), re.IGNORECASE)
    leaks = []
    for directory, _, files in os.walk(PLUGIN):
        for name in files:
            path = os.path.join(directory, name)
            try:
                with open(path, encoding="utf-8") as handle:
                    for number, line in enumerate(handle, 1):
                        for match in pattern.finditer(line):
                            leaks.append(f"{os.path.relpath(path, REPOSITORY)}:{number}: {match.group(0)}")
            except UnicodeDecodeError:
                continue
    for leak in leaks:
        print(leak)
    print(f"{len(leaks)} leak(s)" if leaks else "No leak.")
    return 1 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
