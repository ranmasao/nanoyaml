# Design History

NanoYAML began as a small format boundary for rslab2 artifacts. Its bootstrap
milestones were N0 (canonical emitter), N1 (restricted parser), N2
(round-trip and rejection hardening), and N3 (adoption by corpus inventory).
Those milestones are historical context, not an ongoing roadmap.

The independent NanoYAML repository now owns the implementation, format
contract, tests, and generic design documentation. rslab2 and Conductor own
their schemas and usage of this restricted format.
