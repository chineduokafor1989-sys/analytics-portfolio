"""
Scaffold the analytics portfolio repo.

Usage: run from the root of your cloned (empty) GitHub repo:
    python setup_repo.py

Safe to re-run: existing files are never overwritten.
"""
from pathlib import Path

PROJECTS = ["retail", "finance", "supply-chain", "manufacturing"]
PROJECT_FOLDERS = ["ingestion", "sql", "powerbi", "docs"]
COMMON_FOLDERS = ["config", "sql-templates", "powerbi-theme", "docs-templates"]

GITIGNORE = """\
# Secrets - never commit
.env
*.key
*.pem
local.settings.json

# Python
.venv/
venv/
__pycache__/
*.pyc
.ipynb_checkpoints/

# Local data (raw datasets live in Blob Storage, not in Git)
data/

# Power BI (PBIP keeps model/report as text; ignore local cache and settings)
**/.pbi/localSettings.json
**/.pbi/cache.abf
*.pbix

# OS / editor
.DS_Store
Thumbs.db
.vscode/
"""

ENV_EXAMPLE = """\
# Copy this file to .env and fill in real values. Never commit .env.

# Azure Blob Storage
AZURE_STORAGE_ACCOUNT=
AZURE_STORAGE_KEY=
AZURE_STORAGE_CONTAINER=raw

# Azure SQL Database
SQL_SERVER=yourserver.database.windows.net
SQL_DATABASE=
SQL_USER=
SQL_PASSWORD=
SQL_DRIVER=ODBC Driver 18 for SQL Server
"""

ROOT_README = """\
# Analytics Platform Portfolio

End-to-end analytics projects: ingestion, warehousing, semantic modeling,
reporting, governance and deployment.

## Stack
Azure Blob Storage, Azure SQL Database, Python notebooks, Power BI (PBIP), GitHub.

## Projects
| Project | Status |
|---|---|
| [Retail](retail/) | Planned |
| [Finance](finance/) | Planned |
| [Supply Chain](supply-chain/) | Planned |
| [Manufacturing](manufacturing/) | Planned |

## Repo layout
- `common/` shared assets (date table, report theme, templates)
- `<project>/ingestion` Python notebooks and scripts
- `<project>/sql` schemas, views, stored procedures
- `<project>/powerbi` PBIP semantic model and reports
- `<project>/docs` data dictionary, architecture diagram, lessons learned
"""

PROJECT_README = """\
# {title}

**Status:** Planned

## Goal
_What business questions does this project answer?_

## Architecture
_Add the architecture diagram to `docs/`._

## Data source
_Dataset, license, and link._

## Definition of done
- [ ] Raw data landed in Blob Storage
- [ ] Azure SQL schemas: `{schema}_raw`, `{schema}_core`, `{schema}_mart`
- [ ] Star schema and data dictionary
- [ ] Semantic model with 15+ measures
- [ ] 2-3 reports
- [ ] Lessons learned write-up
"""


def write_if_missing(path: Path, content: str = "") -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")
        print(f"created  {path}")
    else:
        print(f"exists   {path}")


def main() -> None:
    root = Path.cwd()

    write_if_missing(root / ".gitignore", GITIGNORE)
    write_if_missing(root / ".env.example", ENV_EXAMPLE)
    write_if_missing(root / "README.md", ROOT_README)

    for name in COMMON_FOLDERS:
        folder = root / "common" / name
        folder.mkdir(parents=True, exist_ok=True)
        write_if_missing(folder / ".gitkeep")

    for project in PROJECTS:
        for sub in PROJECT_FOLDERS:
            folder = root / project / sub
            folder.mkdir(parents=True, exist_ok=True)
            write_if_missing(folder / ".gitkeep")
        title = project.replace("-", " ").title() + " Analytics"
        schema = project.replace("-", "_")
        write_if_missing(
            root / project / "README.md",
            PROJECT_README.format(title=title, schema=schema),
        )

    print("\nDone. Next: git add . && git commit -m 'Initial structure' && git push")


if __name__ == "__main__":
    main()
