# Remove legacy PUNT_GLOBAL analysis

## Objective
Keep only the `nivel_desempeno` (2021–2024) pipeline in the repository.

## Problem / why
The repo mixed the earlier `PUNT_GLOBAL` regression project (`docs/`, stages 1–9) with the current pipeline. The user asked to remove everything about the previous objective.

## Scope (authorized)
- Delete `docs/` and raw files used only by it.
- Rewrite `README.md` for the 2021–2024 pipeline.
- Remove "previous project" references in `docs_2021_2024/` (04, 05, 07, 11, 19).
- `punt_global` stays: it is the source of `nivel_desempeno`.
- Out of scope: `openspec/`, `docs_2021_2024/pago septiembre.pdf` (untracked, personal), push/PR.

## TDD
Off for this feature: documentation-only, no behavior change. Checks: structural readback, `rg` for leftover references, broken relative links.

## Tasks
- [x] T1 — Delete `docs/`, `ESTU_MEDICINA_3_MODULOS.{csv,xlsx}`, `ESTU_MEDICINA_202607292203.csv`. Route: inline (mechanical `git rm`). Commit `ba1a82e`.
- [x] T2 — Rewrite README + clean references in docs 04, 05, 07, 11, 19; drop unused deps (openpyxl, matplotlib, umap-learn) from requirements.txt. Route: delegated writer (2+ non-trivial files). Checks: legacy-reference `rg` → no matches; relative `.md` links → all targets exist; dependency removal verified by `rg` over scripts/api imports.

## Acceptance
- `rg -i "proyecto anterior|docs/etapa|docs/conclusiones|ESTU_MEDICINA_3_MODULOS"` returns nothing outside `odd/`.
- README describes only the 2021–2024 pipeline with correct reproduction steps.

## Next step
Done. Push/PR is the user's decision.
