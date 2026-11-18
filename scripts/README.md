# Optional execution tools

The core CLI works offline. These opt-in tools help capture source audits or actual external model responses; they do not judge correctness, create independent reviews, or certify a task as ready.

| Script | External requirement | Output |
| --- | --- | --- |
| `run_source_audit.py` | `curl` and public network access | A real release-date source audit, command logs, reports, and checksums. |
| `run_haiku.py` | Installed, authenticated Claude Code CLI | Prompt, model labels reported by the CLI, answer, reduced events, and checksums. |
| `run_codex.py` | Installed, authenticated Codex CLI | Prompt, answer, reduced events, model-identity limits, and checksums. |

Run from the repository root. Model invocations consume the configured account allowance. No credentials are bundled or read directly by these scripts. Supply only data you are authorized to send to the selected service.

```sh
python3 scripts/run_source_audit.py --output runs/release-date-audit

python3 scripts/run_haiku.py \
  --task examples/release-dates/source-audit/package/task.json \
  --model haiku --output runs/haiku-release-dates

python3 scripts/run_codex.py \
  --task examples/release-dates/source-audit/package/task.json \
  --output runs/codex-release-dates
```

Every output directory must be fresh. `runs/` is ignored by Git: inspect and curate a relevant record before intentionally publishing it. Failed authentication, missing responses, or timeouts are infrastructure problems, not model mistakes. The Haiku alias can resolve differently over time; inspect the reported model labels. Do not infer an unreported provider model identifier.

Both model runners read the task's `prompt`, append public-web/citation instructions and a prohibition on local-file access, and run from an isolated temporary directory. The reference answer is not passed to the model. Codex uses its read-only sandbox; Claude exposes only web tools and disables hooks and extra MCP servers. These are different execution environments, not a controlled model comparison.

Reduced event exports omit private reasoning, thread/session identifiers, and third-party response bodies. Metadata records the actual CLI version and flags. The response remains unassessed until someone checks its claims and consulted sources. The runners do not emit complete EvidenceTrail screening-import records automatically; use the [screening data model](../docs/data-model.md) to record actual findings before `attach-screening`.
