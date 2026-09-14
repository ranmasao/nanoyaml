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


def test_0_1_0_canonical_output_is_preserved():
    cases = [
        ({"key": "value"}, '"key": "value"\n'),
        (
            {"outer": {"inner": {"value": "text"}}},
            '"outer":\n  "inner":\n    "value": "text"\n',
        ),
        (
            {"items": ["one", 0, -1]},
            '"items":\n  - "one"\n  - 0\n  - -1\n',
        ),
        (
            {"items": [{"name": "A"}, {"name": "B"}]},
            '"items":\n  - "name": "A"\n  - "name": "B"\n',
        ),
        (
            {"items": [[1, 2], ["three"]]},
            '"items":\n  -\n    - 1\n    - 2\n  -\n    - "three"\n',
        ),
        (
            {"text": 'quote " slash \\ newline\n tab\t'},
            '"text": "quote \\" slash \\\\ newline\\n tab\\t"\n',
        ),
        ({"text": "Привет ☃"}, '"text": "Привет ☃"\n'),
        ({"zero": 0, "negative": -2026}, '"zero": 0\n"negative": -2026\n'),
    ]
    for value, expected in cases:
        assert nanoyaml.dumps(value) == expected


def test_accepted_noncanonical_spelling_is_canonicalized():
    parsed = nanoyaml.loads('"key":   "value"\r\n')
    assert parsed == {"key": "value"}
    assert nanoyaml.dumps(parsed) == '"key": "value"\n'


def test_empty_sequences_are_supported_and_canonical():
    value = {"items": [], "nested": {"empty": []}}
    assert nanoyaml.loads(nanoyaml.dumps(value)) == value
    assert nanoyaml.dumps(value) == (
        '"items": []\n'
        '"nested":\n'
        '  "empty": []\n'
    )


def test_empty_sequences_inside_sequences_are_canonical():
    value = {"items": [[], ["A"]]}
    assert nanoyaml.loads(nanoyaml.dumps(value)) == value
    assert nanoyaml.dumps(value) == '"items":\n  - []\n  -\n    - "A"\n'


def test_flow_sequences_load_and_canonicalize_to_block_form():
    text = '"items": [ "A" , "B", 17, -2, 0 ]\n'
    assert nanoyaml.loads(text) == {"items": ["A", "B", 17, -2, 0]}
    assert nanoyaml.dumps(nanoyaml.loads(text)) == (
        '"items":\n  - "A"\n  - "B"\n  - 17\n  - -2\n  - 0\n'
    )


def test_nested_flow_sequences_load():
    assert nanoyaml.loads('"items": [["A"], [], ["B", 17]]\n') == {
        "items": [["A"], [], ["B", 17]]
    }


def test_flow_sequences_inside_block_sequences_load():
    text = '"outer":\n  - ["A", "B"]\n  - ["C"]\n'
    assert nanoyaml.loads(text) == {"outer": [["A", "B"], ["C"]]}


def test_flow_sequence_surrogate_escapes_are_rejected():
    for escaped in (r"\uD800", r"\uDE00"):
        with pytest.raises(nanoyaml.NanoYAMLError, match=r"line 1"):
            nanoyaml.loads(f'"items": ["{escaped}"]\n')


def test_empty_sequence_in_mapping_sequence_item_has_canonical_layout():
    value = {"items": [{"name": "A", "dependencies": []}]}
    expected = '"items":\n  - "name": "A"\n    "dependencies": []\n'
    assert nanoyaml.dumps(value) == expected
    assert nanoyaml.loads(expected) == value


def test_flow_sequence_rejects_all_trailing_content():
    for character in (
        " ",
        "\t",
        "\x0b",
        "\x0c",
        "\u00a0",
        "\u0085",
        "\u2028",
        "\u2029",
    ):
        with pytest.raises(nanoyaml.NanoYAMLError):
            nanoyaml.loads(f'"items": ["A"]{character}\n')


def test_unicode_line_separator_characters_are_quoted_content():
    value = {"text": "A\u0085B\u2028C\u2029D"}
    text = '"text": "A\u0085B\u2028C\u2029D"\n'
    assert nanoyaml.loads(text) == value
    assert nanoyaml.dumps(value) == text


def test_raw_control_characters_are_rejected_but_escaped_controls_are_valid():
    for character in ("\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x00"):
        with pytest.raises(nanoyaml.NanoYAMLError):
            nanoyaml.loads(f'"key": {character}\n')
        with pytest.raises(nanoyaml.NanoYAMLError):
            nanoyaml.loads(f'"key": "before{character}after"\n')
    assert nanoyaml.loads('"key": "before\\u0000after"\n') == {
        "key": "before\x00after"
    }


def test_yaml_forbidden_output_characters_are_escaped_without_ascii_mode():
    value = {"text": "\x7f\x80\x84\x86\x9f\ufffe\uffff Привет ☃"}
    assert nanoyaml.dumps(value) == (
        '"text": "\\u007F\\u0080\\u0084\\u0086\\u009F\\uFFFE\\uFFFF '
        'Привет ☃"\n'
    )


def test_escaped_quoted_characters_load_and_canonicalize():
    text = '"text": "\\u007f\\u0080\\u009f\\ufffe\\uffff"\n'
    assert nanoyaml.loads(text) == {
        "text": "\x7f\x80\x9f\ufffe\uffff"
    }
    assert nanoyaml.dumps(nanoyaml.loads(text)) == (
        '"text": "\\u007F\\u0080\\u009F\\uFFFE\\uFFFF"\n'
    )


def test_raw_quoted_characters_are_canonicalized_when_required():
    value = {"text": "raw \x7f\x80\x9f\ufffe\uffff"}
    text = '"text": "raw \x7f\x80\x9f\ufffe\uffff"\n'
    assert nanoyaml.loads(text) == value
    assert nanoyaml.dumps(value) == (
        '"text": "raw \\u007F\\u0080\\u009F\\uFFFE\\uFFFF"\n'
    )


@pytest.mark.parametrize(
    "text",
    [
        '"items": [true]\n',
        '"items": [false]\n',
        '"items": [null]\n',
        '"items": [1.0]\n',
        '"items": [-1.5]\n',
        '"items": [1e3]\n',
        '"items": [NaN]\n',
        '"items": [Infinity]\n',
        '"items": [-Infinity]\n',
        '"items": [{"a": 1}]\n',
        '"items": [["A", true]]\n',
        '"items": [["A", {"b": 1}]]\n',
        '"items": [plain]\n',
        '"items": [\'single\']\n',
        '"items": [&x "A"]\n',
        '"items": [*x]\n',
        '"items": [!!str "A"]\n',
        '"items": ["A",]\n',
        '"items": [, "A"]\n',
        '"items": ["A",, "B"]\n',
        '"items": ["A" "B"]\n',
        '"items": ["A"\n',
        '"items": ["A"] trailing\n',
        '"items": ["A": "B"]\n',
        r'"items": ["bad\q"]' + "\n",
        '"items": ["unterminated]\n',
        '"items": [-0]\n',
        '"items": [01]\n',
        '"items": [-01]\n',
    ],
)
def test_flow_sequences_reject_values_and_syntax_outside_contract(text):
    with pytest.raises(nanoyaml.NanoYAMLError):
        nanoyaml.loads(text)


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
    text = '\n  \n"name": "example"\n\n"items":\n  - "alpha"\n\n'
    value = nanoyaml.loads(text)
    assert value == {"name": "example", "items": ["alpha"]}
    assert nanoyaml.dumps(value) == (
        '"name": "example"\n"items":\n  - "alpha"\n'
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


def test_root_sequences_and_empty_root_mappings_are_rejected():
    for value in ([], {}):
        with pytest.raises(nanoyaml.NanoYAMLError):
            nanoyaml.dumps(value)


def test_empty_mappings_remain_rejected():
    for value in ({"empty": {}}, {"empty": {"nested": {}}}):
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
