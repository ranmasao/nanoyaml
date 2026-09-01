import pytest

import nanoyaml


def test_round_trip_and_canonical_output():
    value = {"items": ["one", 2, {"nested": "value"}], "text": "unicode \u2603"}
    encoded = nanoyaml.dumps(value)
    assert nanoyaml.loads(encoded) == value
    assert nanoyaml.dumps(nanoyaml.loads(encoded)) == encoded


def test_blank_lines_are_accepted_and_not_emitted():
    text = '\n  \n"type": "conductor.project"\n\n"common":\n  - "README.md"\n\n'
    value = nanoyaml.loads(text)
    assert value == {"type": "conductor.project", "common": ["README.md"]}
    assert nanoyaml.dumps(value) == (
        '"type": "conductor.project"\n"common":\n  - "README.md"\n'
    )


def test_error_line_numbers_skip_blank_lines():
    with pytest.raises(nanoyaml.NanoYAMLError, match=r"line 4:"):
        nanoyaml.loads('\n\n"ok": 1\n"bad": plain\n')


def test_whitespace_only_document_is_rejected():
    with pytest.raises(nanoyaml.NanoYAMLError, match=r"line 1:"):
        nanoyaml.loads(" \n\t\n")


@pytest.mark.parametrize(
    "text",
    [
        "",
        "- 1\n",
        '"key": true\n',
        '"key": 1.0\n',
        '"key": []\n',
        '"key": plain\n',
        '---\n"key": 1\n',
    ],
)
def test_rejects_broader_yaml(text):
    with pytest.raises(nanoyaml.NanoYAMLError):
        nanoyaml.loads(text)


def test_rejects_unsupported_values_and_empty_collections():
    for value in (None, True, 1.5, [], {}, {"items": []}):
        with pytest.raises(nanoyaml.NanoYAMLError):
            nanoyaml.dumps(value if isinstance(value, dict) else {"bad": value})
