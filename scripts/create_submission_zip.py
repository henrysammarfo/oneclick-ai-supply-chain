import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "submission" / "oneclick-ai-supply-chain.zip"

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    "logs",
    "submission",
    ".claude",
    ".cloud",
    ".eab",
    ".EAB",
}
EXCLUDE_FILES = {
    ".mcp.json",
    "supply_graph.json",
}
EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
    ".sqlite3",
    ".db",
}


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if rel.name.startswith(".env") and rel.name != ".env.example":
        return True
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    if rel.name in EXCLUDE_FILES:
        return True
    if rel.suffix in EXCLUDE_SUFFIXES:
        return True
    if rel.name.endswith(".zip") and parts and parts[0] == "submission":
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a clean submission zip.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output zip path (default: submission/oneclick-ai-supply-chain.zip)",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in ROOT.rglob("*"):
            if path.is_dir():
                continue
            if should_skip(path):
                continue
            zf.write(path, path.relative_to(ROOT))
            count += 1

    print(f"Wrote {output} with {count} files")


if __name__ == "__main__":
    main()
