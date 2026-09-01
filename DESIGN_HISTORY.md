# Design History

## Origin and status

NanoYAML originally emerged from rslab2 corpus-analysis work. It was created
as a small format boundary for generated and curated laboratory artifacts,
not as a general YAML compatibility layer. The bootstrap milestones N0 through
N3 are complete historical milestones. This document preserves their design
rationale; it is not an active execution queue.

The original design goal was:

```text
small Python values
    -> one canonical textual representation
    -> valid YAML
    -> small deterministic parser/emitter
```

The independent NanoYAML repository is now the owner of this implementation,
format contract, generic tests, and generic documentation. Consumer projects
own their schemas and the meaning of their artifacts.

## Restricted subset principle

NanoYAML is a restricted YAML subset, not a competing dialect. Every emitted
document should be valid ordinary YAML, but the NanoYAML parser accepts only
the documented subset. Restriction is intentional: a small accepted language
is easier to inspect, validate, diff, and keep deterministic than a broad YAML
interoperability surface.

The data model is deliberately conservative:

```text
mapping with string keys
sequence
double-quoted string
integer
```

Boolean and null values were not added merely for completeness. An extension
should be driven by a real artifact that cannot be represented comfortably,
and should be introduced as an explicit contract decision.

The parser and emitter operate on ordinary Python values. Artifact schemas and
validation remain outside NanoYAML. For example, NanoYAML knows only mappings,
sequences, strings, and integers; a consumer knows fields such as
`goldcorpus_commit`, `surface`, or `count`.

## Canonical representation

The emitter owns one canonical text representation for each supported value:

```text
UTF-8
LF newlines
2-space indentation
final newline
mapping insertion order preserved
sequence order preserved
double-quoted and deterministically escaped strings
plain decimal integers
no emitted comments or blank lines
```

Canonicalization intentionally does not preserve arbitrary source formatting.
Input may contain harmless blank or whitespace-only physical lines, including
leading, trailing, and inter-element lines. Those lines are ignored, while
diagnostic locations retain their original physical line numbers. A document
containing only whitespace is still empty and is rejected.

The format intentionally rejects anchors and aliases, tags, directives, flow
collections, implicit scalar typing, unquoted strings, floating-point values,
timestamps, multiline scalar styles, merge keys, comments, external includes,
empty collections, and arbitrary object serialization. These are non-goals,
not missing compatibility work.

## Bootstrap milestones

### N0 - contract and canonical emitter

N0 froze the first executable subset based on actual inventory needs and added
a small stdlib-only canonical emitter. The initial value model was limited to
nested mappings, sequences, double-quoted strings, and integers. Tests covered
escaping, indentation, Unicode, collection validation, deterministic output,
and unsupported Python values.

### N1 - restricted parser

N1 added a parser for exactly the N0 subset. It produces ordinary Python
mappings, sequences, strings, and integers, rejects syntax outside the subset,
and reports line-oriented errors for malformed indentation, malformed quoted
strings, duplicate keys, and unsupported constructs. It never performs
implicit YAML typing.

### N2 - round-trip and rejection hardening

N2 established the boundary properties:

```text
supported value -> dump -> load -> same supported value
canonical text -> load -> dump -> byte-identical canonical text
```

Adversarial tests were added for implicit scalars, anchors and aliases, flow
syntax, multiline scalars, tabs, malformed escapes, duplicate keys, comments,
document markers, and invalid indentation. Any future extension must be
justified by concrete artifact pressure rather than YAML feature completeness.

### N3 - initial consumer adoption

N3 replaced hand-written inventory serialization with the NanoYAML emitter and
used the parser in validation where useful. Inventory schema ownership stayed
with corpus analysis. The resulting boundary was made available to curated
lexical artifacts, RatIL fixtures, and other consumers whose data shapes fit
the restricted contract.

## Relationship to corpus analysis

The historical bootstrap sequence was:

```text
Corpus Analysis M0 - deterministic inventory
    -> NanoYAML N0..N3
    -> Corpus Analysis M1 - read-only human inspection
```

That sequence is complete. The corpus-analysis project owns its current
research and implementation order; NanoYAML remains a supporting component,
not a corpus-analysis department or language-processing layer.

## Extension policy and non-goals

When a future artifact does not fit, first reconsider the artifact shape.
Extend NanoYAML only for demonstrated need, with focused tests and an explicit
contract update. Do not add a feature because it is common in full YAML.

NanoYAML does not aim to provide arbitrary YAML interoperability, PyYAML API
compatibility, comment or formatting round-tripping, schema validation,
dataclass or object serialization, streaming/event APIs, plugin hooks, or
performance optimization beyond small laboratory artifacts. Its value is
smallness, determinism, inspectability, and a deliberately narrow boundary.
