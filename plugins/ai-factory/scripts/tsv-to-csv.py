"""Converts the tsv output of db-mysql.sh to a CSV Excel opens directly: ';' separator, UTF-8 with BOM."""
import csv
import sys

MYSQL_NULL = "NULL"


def convert(source: str, target: str) -> int:
    rows = 0
    with open(source, encoding="utf-8") as reader, open(target, "w", encoding="utf-8-sig", newline="") as output:
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        for line in reader:
            fields = line.rstrip("\n").split("\t")
            # The batch client escapes tabs and newlines inside values; make them readable again.
            writer.writerow(
                "" if field == MYSQL_NULL else field.replace("\\t", " ").replace("\\n", " ").replace("\\\\", "\\")
                for field in fields
            )
            rows += 1
    return rows


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: tsv-to-csv.py <input.tsv> <output.csv>")
    total = convert(sys.argv[1], sys.argv[2])
    print(f"{max(total - 1, 0)} data rows (+ header) written to {sys.argv[2]}")
