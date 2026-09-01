# NanoYAML

NanoYAML is a small, deterministic parser and emitter for a deliberately
restricted YAML subset. It converts small Python values to one canonical text
representation and accepts that representation plus harmless whitespace
variation.

## Contract

Supported values are non-empty mappings with string keys, non-empty sequences,
double-quoted strings, and integers. Mapping insertion order and sequence order
are preserved. Output uses UTF-8 text, LF newlines, two-space indentation, a
final newline, quoted strings, decimal integers, and no blank lines or comments.

Input accepts blank and whitespace-only physical lines, including leading,
trailing, and inter-element lines. `loads()` ignores those lines but diagnostics
retain their original physical line numbers. A whitespace-only document is
still rejected.

The parser intentionally rejects comments, flow collections, unquoted strings,
implicit scalar typing, floats, anchors, aliases, tags, directives, multiline
scalars, and empty collections. NanoYAML is not a general YAML implementation.

## API

```python
from nanoyaml import NanoYAMLError, dumps, loads
```

`dumps(value)` returns canonical text. `loads(text)` returns ordinary Python
`dict`, `list`, `str`, and `int` values. Both raise `NanoYAMLError` for values
or syntax outside this contract.

## Development

The package is at the repository root so it can be mounted directly as a
submodule at a consumer's existing `nanoyaml` package path. Run `python -m
pytest` for the standalone tests and `python -m ruff check .` when Ruff is
available.
