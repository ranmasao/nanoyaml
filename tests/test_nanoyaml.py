import nanoyaml
import pytest


def test_canonical_values_round_trip_byte_identically():
    values = [
        {"zero": 0, "negative": -12, "positive": 2026},
        {"nested": {"first": {"second": "value"}, "last": "end"}},
        {"items": ["one", 0, -1, {"mapping": {"nested": "value"}}]},
        {"items": [{"first": 1, "second": 2}, {"sequence": ["two"]}]},
        {"text": "unicode \u2603 and escapes \" \\ \n \t"},
    ]
    for value in values:
        encoded = nanoyaml.dumps(value)
        assert nanoyaml.loads(encoded) == value
        assert nanoyaml.dumps(nanoyaml.loads(encoded)) == encoded


def test_accepted_noncanonical_spelling_is_canonicalized():
    parsed = nanoyaml.loads('"key":   "value"\r\n')
    assert parsed == {"key": "value"}
    assert nanoyaml.dumps(parsed) == '"key": "value"\n'


def test_loads_round_trips_nested_shapes():
    values = [
        {"name": "demo", "items": ["one", 2, {"enabled": "yes"}]},
        {"items": [{"mapping": {"nested": "value"}}, {"sequence": [1]}]},
        {"nested": [[1, 2], ["three"]]},
        {"first": {"second": {"third": "value"}}, "last": -12},
    ]
    for value in values:
        assert nanoyaml.loads(nanoyaml.dumps(value)) == value


def test_loads_scalars_and_escapes():
    value = {
        "text": (
            '\u0401\u043b\u043a\u0430 "path" \\\ntab\t\b\f\r '
            "null yes true 12 2026-08-22"
        ),
        "zero": 0,
        "negative": -7,
    }
    assert nanoyaml.loads(nanoyaml.dumps(value)) == value


def test_json_escaped_slash_is_tolerated_and_canonicalized():
    parsed = nanoyaml.loads('"key": "a\\/b"\n')
    assert parsed == {"key": "a/b"}
    assert nanoyaml.dumps(parsed) == '"key": "a/b"\n'


def test_unicode_and_escaping():
    value = {"text": '\u0401\u043b\u043a\u0430 "path" \\\ntab\t null yes 12'}
    expected = (
        '"text": "\u0401\u043b\u043a\u0430 \\"path\\" '
        + "\\\\"
        + "\\ntab\\t null yes 12\"\n"
    )
    assert nanoyaml.dumps(value) == expected


def test_order_is_preserved():
    value = {"z": [3, 1], "a": {"second": 2, "first": 1}}
    assert nanoyaml.dumps(value) == (
        '"z":\n  - 3\n  - 1\n"a":\n'
        '  "second": 2\n  "first": 1\n'
    )


def test_nested_collections_in_mapping_sequence_items():
    value = {"items": [{"mapping": {"nested": "value"}}, {"sequence": [1]}]}
    assert nanoyaml.dumps(value) == (
        '"items":\n'
        '  - "mapping":\n'
        '      "nested": "value"\n'
        '  - "sequence":\n'
        '      - 1\n'
    )


def test_blank_lines_are_accepted_and_not_emitted():
    text = '\n  \n"type": "conductor.project"\n\n"common":\n  - "README.md"\n\n'
    value = nanoyaml.loads(text)
    assert value == {"type": "conductor.project", "common": ["README.md"]}
    assert nanoyaml.dumps(value) == (
        '"type": "conductor.project"\n"common":\n  - "README.md"\n'
    )


def test_blank_lines_preserve_physical_error_line_numbers():
    with pytest.raises(nanoyaml.NanoYAMLError, match=r"line 12:"):
        nanoyaml.loads('\n' * 11 + '"key": plain\n')


def test_whitespace_only_document_is_rejected():
    with pytest.raises(nanoyaml.NanoYAMLError, match=r"line 1:"):
        nanoyaml.loads(" \n\t\n")


@pytest.mark.parametrize(
    "text",
    [
        "",
        "  \n",
        "- 1\n",
        '"key": plain\n',
        '"key": true\n',
        '"key": null\n',
        '"key": 01\n',
        '"key": 1.0\n',
        '"key": 0x10\n',
        '"key": [1]\n',
        '"key": {"nested": "value"}\n',
        '"key": &anchor\n',
        '"key": *anchor\n',
        '"key": !!str "value"\n',
        '%YAML 1.2\n"key": "value"\n',
        '---\n"key": "value"\n',
        '...\n"key": "value"\n',
        '"key": |\n  value\n',
        '"key": >\n  value\n',
        '"key": "value" # comment\n',
        '"key": "value" trailing\n',
        '"key": "bad\\q"\n',
        '"key": "bad\\x20"\n',
        '"key":\n  - "value"\n  # comment\n',
        'key: "value"\n',
        '"key": \'value\'\n',
    ],
)
def test_loads_rejects_unsupported_yaml_syntax(text):
    with pytest.raises(nanoyaml.NanoYAMLError):
        nanoyaml.loads(text)


def test_surrogate_escapes_are_rejected():
    for escaped in (r"\uD800", r"\uDE00"):
        with pytest.raises(nanoyaml.NanoYAMLError, match=r"line 1"):
            nanoyaml.loads(f'"key": "{escaped}"\n')


def test_duplicate_keys_are_rejected_at_all_mapping_levels():
    invalid = [
        '"key": 1\n"key": 2\n',
        '"items":\n  - "a": 1\n    "a": 2\n',
        '"outer":\n  "inner": 1\n  "inner": 2\n',
    ]
    for text in invalid:
        with pytest.raises(nanoyaml.NanoYAMLError):
            nanoyaml.loads(text)


def test_invalid_indentation_and_tabs_are_rejected():
    invalid = [
        '"outer":\n    "inner": 1\n',
        '"items":\n  -\n    "value": 1\n   "other": 2\n',
        '"items":\n  - "first"\n    "second": 2\n',
        '"key":\n\t"nested": "value"\n',
    ]
    for text in invalid:
        with pytest.raises(nanoyaml.NanoYAMLError):
            nanoyaml.loads(text)


def test_malformed_root_and_empty_collections_are_rejected():
    for value in ([], {}, {"empty": []}, {"empty": {}}):
        with pytest.raises(nanoyaml.NanoYAMLError):
            nanoyaml.dumps(value)


def test_unsupported_python_values_are_rejected():
    for value in (None, True, 1.5, b"bytes", (1,), {1}, object()):
        with pytest.raises(nanoyaml.NanoYAMLError):
            nanoyaml.dumps({"bad": value})
    with pytest.raises(nanoyaml.NanoYAMLError):
        nanoyaml.dumps({1: "bad"})
    with pytest.raises(nanoyaml.NanoYAMLError):
        nanoyaml.dumps({"nested": ["ok", None]})


def test_dumps_is_deterministic():
    value = {"first": ["x", 1], "second": {"nested": "y"}}
    assert nanoyaml.dumps(value) == nanoyaml.dumps(value)


def test_loads_rejects_non_string_input():
    with pytest.raises(TypeError):
        nanoyaml.loads(None)
