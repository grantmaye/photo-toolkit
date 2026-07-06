# Contributing

Thanks for helping improve `photo-toolkit`.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,heic]"
pytest
```

## Principles

- Keep commands safe by default.
- Preserve dry-run behavior.
- Do not hardcode private paths or personal workflows.
- Add reports for any metadata-changing or destructive action.
- Prefer moving files over deleting files.
- Add tests for safety behavior and filename/date planning logic.

## Pull requests

Include a short description, test results, and any safety implications.
