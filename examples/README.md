# Examples

These examples demonstrate EvidenceTrail's authoring, evidence-audit, and review workflow.

| Example | What it demonstrates | Status |
| --- | --- | --- |
| [Fictional task](fictional-task.json) and [offline demo](offline_demo.py) | Package fields, form rendering, fingerprints, and validation rejection. | Synthetic; never a real submission. |
| [Release-date research](release-dates/README.md) | A real source audit and a separate model response against two official historical records. | Sources verified; model answered correctly; three failure screenings and independent review are incomplete. |

Run the offline demonstration with `python3 examples/offline_demo.py`. Network/model runs are opt-in; see [runner scripts](../scripts/README.md). Fresh outputs belong in the ignored `runs/` directory. Only curated, relevant evidence belongs in `examples/`.
