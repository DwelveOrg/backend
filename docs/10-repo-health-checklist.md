# 10 - Repo Health Checklist

## Current Status

This backend checkout is currently clean:

- no tracked `__pycache__` files
- no tracked local database files
- no tracked IDE files
- no tracked certificate files
- `.gitignore` covers common local junk

## Local Setup

Install Python 3.12 or 3.13 and confirm one of these works:

```powershell
python --version
```

or:

```powershell
py --version
```

Create a local virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Sanity Checks

Run the test suite:

```powershell
python -m pytest
```

Check git cleanliness:

```powershell
git status --short --ignored
```

Confirm ignored junk is not tracked:

```powershell
git ls-files -ci --exclude-standard
```

The second command should return no output.

## Optional Cleanup

If local cache folders appear again, you can remove them safely:

```powershell
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

If local `.db` files are recreated for development, that is fine. They should remain untracked as long as `.gitignore` stays in place.
