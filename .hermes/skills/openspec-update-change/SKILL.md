---
name: openspec-update-change
description: Update an OpenSpec change by revising its existing planning artifacts and keeping them coherent with one another. Use when the user wants to revise a change's plan, fold new decisions into it, or reconcile its artifacts after an edit. Also use when the user says "openspec update change" or "opsx update". If the user means the openspec update CLI command, which refreshes generated files, run that command instead. Never edits code.
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.16.1"
---

## プロジェクト固有ルール: USDM 仕様書とワークフロー（USDM ＋ 1サブタスク＝1コミット規約）

このリポジトリは MachinakaRestaurantSupportTools 全体システムの管理拠点で、OpenSpec は **`usdm` スキーマ**（`proposal` → `usdm` → `specs` → `design` → `tasks`）を使用します。以下のルールは上記の記述と矛盾する場合、こちらを優先してください。

- **日本語記述と USDM スキーマ準拠**:
  - OpenSpec アーティファクト（`proposal.md`, `usdm.md`, `specs/**/spec.md`, `design.md`, `tasks.md`）および対話はすべて日本語で記述する。
  - `proposal.md`: `## Why` セクションは50文字以上1000文字以内で背景・目的を簡潔に記述する。
  - `usdm.md`: `affordd-prj/usdm-schema` のマークダウン形式定義（H1〜H6の固定見出し階層、全角山括弧 `＜＞`、仕様項目の `- □□□ **Sxx-yy-zz**:` ラベル）を厳守する。
  - `specs/**/spec.md`: `openspec validate --strict` を通過させるため、各 `### Requirement:` 本文は500文字以内に収め、文中に必ず半角大文字の `SHALL` または `MUST` を含める。見出しには変更固有の連番（`R01` 等）を含めず恒久的な名前とし、直下の行に `**USDM**: R01-01` を記載する。各 `#### Scenario:` には必ず `**WHEN**`（または `**GIVEN**`）と `**THEN**` の両方を含める。
- **仕様の正本（`usdm/`）と設計**:
  - 正本は `usdm/` 配下の9プロジェクト: 全体 = `usdm/machinaka_restaurant_support_tools/`、サブシステム8件 = `usdm/accounting_management/`・`usdm/dine_in_ordering/`・`usdm/guest_management/`・`usdm/menu_management/`・`usdm/order_management/`・`usdm/product_management/`・`usdm/sales_management/`・`usdm/takeout_ordering/`。記法は `../md2usdm/MANUAL.md`、完成例は `../md2usdm/examples/` を参照。
  - 全体システム設計は `docs/system-design.md`。仕様変更時は連携ポイント（結合試験範囲 I-1〜）・テスト戦略との整合も確認する。
  - `usdm/` 配下の仕様 Markdown を追加・変更した後は、必ず `../.venv/bin/md2usdm usdm/<プロジェクト>` で Excel を再生成する（仮想環境は `../.venv`、`.xlsx` は `.gitignore` 済みでコミット対象外）。
- **タスク粒度と 3種のタスク（`tasks.md`）**:
  - 各チェックボックス項目（`- [ ] X.Y [Sxx-yy-zz] ...`）は **「1サブタスク ＝ 1コミット」** の粒度（変更ファイル数1〜5個程度、単独で検証・テストが通る最小単位）に分解する。
  - フォーマッタ実行、Linter自動修正、`sed` 等による一括置換、パッケージ追加などの「コマンド実行による機械的な変更」は、手書きのロジック変更や仕様記述とは別の独立した1サブタスク（＝1コミット）として切り出す。
  - タスクは「各サブシステムリポジトリへの実装委譲指示（対象リポジトリ・参照 USDM パス・単体試験までの完了条件を明記）」「サブシステム PR の確認」「このリポジトリでの結合試験・総合試験」の3種に区別して書く。
- **実装・コミット規約（1サブタスク ＝ 1コミット）**:
  - `apply` フェーズでは、`tasks.md` のチェックボックス1項目（1サブタスク）を完了するごとに、単独で検証・テストがパスする状態（Green State）を確認し、該当ファイルと `tasks.md` のチェック更新（`- [ ]` → `- [x]`）を含めて **必ず1サブタスクにつき1コミット** を作成する（複数サブタスクを1コミットにまとめることは厳禁）。
  - 機械的変更と手動実装は完全に分離し、それぞれ独立した1コミットとして切り出す。
  - コミットメッセージは1行目を `<type>(<scope>): <サブタスクの要約>` とし、本文に `Why:` と `What:` を記述し、末尾の Git Trailers に `Issue: #<Issue番号（該当なしは N/A）>` / `Task: <サブタスク識別子とUSDM仕様ID（例: 1.1 [S01-03-02]）>` / `Verification: <確認コマンド>` / `Executed-Command: <機械的変更時の実行コマンド全文、手動変更時は "manual">` を必ず記載する。
- **opsx フローとアーカイブ時USDMラベル更新**:
  - **propose**: 最初にブランチ `feature/<change-id>`（change 名と一致）を作成してからアーティファクトに着手する。
  - **apply**: `tasks.md` の各サブタスクを「1サブタスク ＝ 1コミット」規約に従って順次実施・コミットする。全サブタスク完了後、全体テストおよび `openspec validate <change-name> --strict` の通過を確認する。
  - **archive**: 各サブシステムの単体試験状況（PR 状態）を確認し、結合試験・総合試験を実施する。完了して閉じるタスク（`- [x]`）に対応する `usdm.md` 内の各仕様（`Sxx-yy-zz`）について、レビュー・実装・テストの完了状態に応じた USDM 仕様ラベルのチェック（`□□□` → `■□□` レビュー済み / `■■□` 実装済み / `■■■` テスト済み）を入れて `usdm.md` を更新・コミットし、`openspec validate <change-name> --strict` を通過させてからアーカイブする。完了で当該ブランチの GitHub プルリクエスト作成を提案する（`git push` / PR 作成はユーザーの明示的な指示でのみ実行し、結合・総合試験が完了するまで main にマージしない。main マージ時は各サブシステム側の submodule 参照コミットを更新する）。


Revise a change's existing planning artifacts and keep them coherent. Never edit code.

**Store selection:** If the user names a store (a store is a standalone OpenSpec repo registered on this machine) or the work lives in one, run `openspec store list --json` to discover registered store ids, then pass `--store <id>` on the commands that read or write specs and changes (`new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`, `schemas`, `view`). Once selected, treat `--store <id>` as sticky for the rest of the workflow. Every unscoped example of those commands below is shorthand: before running it, append the flag. For example, run `openspec status --change "<name>" --json --store "<id>"`, not the unscoped form shown below. Other commands do not take the flag. Hints printed by commands already carry the flag; keep it on follow-ups. Without a store, commands act on the nearest local `openspec/` root.

**Project check:** These steps expect a project that already uses OpenSpec. Before the first step that writes anything (`new change`, `archive`, `sync specs`, or authoring an artifact file), confirm the project has a root: run `openspec list --json` (with `--store <id>` when a store is selected, since the store is then the root) and read `root`. A root object means the project is set up. `"root": null` means it is not - there is no `openspec/` directory here, and a write such as `openspec new change` would create one as a side effect. The command also exits non-zero, which is that answer rather than a broken CLI, so read the JSON instead of retrying or working around it.

One `"root": null` is not about setup: when a `status` error message starts with `Declared in` or `Invalid store declaration in` and names this project's `openspec/config.yaml` (or `config.yml`), the project does use OpenSpec through a store it declares, which this machine cannot resolve (the store is not registered, or the `store:` line is malformed). Do not treat it as uninitialized and skip the branches below: stop before writing and show the user that error's `message` and `fix`.

Otherwise, with no root, what happens next depends on how this workflow was reached:

- **Auto-selected**: you chose this workflow yourself, without the user naming OpenSpec, naming this skill, or running its slash command. Stop using OpenSpec and answer the request normally, as you would with no OpenSpec installed. Do not ask them to set anything up and do not mention OpenSpec setup.
- **Explicit OpenSpec request**: the user named OpenSpec, named this skill, or ran its slash command. Stop before writing and ask how to proceed: set this project up (`openspec init`), target a store they already have (`--store <id>`), or continue without OpenSpec for this request. Wait for their answer.

In both branches, never create the root as a side effect: do not run `openspec init` until the user asks for it, do not hand-create `openspec/` files, and do not let a command create it.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

This workflow revises artifacts that already exist; it never creates missing ones. When an artifact is missing, `openspec status --change "<name>" --json` names the next one and `openspec instructions "<artifact-id>" --change "<name>" --json` explains how to write it.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes sorted by most recently modified, and ask the user to select one

   When prompting, present the top 3-4 most recently modified changes as options, showing:
   - Change name
   - Status (e.g., "0/5 tasks", "complete", "no tasks")
   - How recently it was modified (from `lastModified` field)

   Mark the most recently modified change as "(Recommended)" since it's likely what the user wants to update.

   Always announce: "Using change: <name>" and how to override (e.g., `/openspec-update-change <other>`).

2. **Get the change's artifacts**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to understand current state. The response includes:
   - `schemaName`: The workflow schema being used (e.g., "spec-driven")
   - `artifacts`: Array of artifacts with their status ("done", "skipped", "ready", "blocked")
   - `isPlanningComplete`: Boolean indicating if all planning artifacts are complete. Older CLI versions expose the same value as `isComplete`.
   - `planningHome`, `changeRoot`, `artifactPaths`, and `actionContext`: path and scope context. Use these instead of assuming repo-local paths.

   The artifact ids and paths come from the active schema - do NOT assume them, and do NOT branch on hardcoded artifact names. Custom schemas must work unchanged.

   The files to edit are `artifactPaths.<id>.existingOutputPaths` - the concrete files that exist on disk, already glob-expanded for glob artifacts (e.g. `specs/**/*.md`), plus any confirmed concrete path allowed under a partly populated glob artifact (step 4). Do NOT write to `resolvedOutputPath`: for a glob artifact it is still the glob pattern, not a real file.

3. **Understand the request**
   - If the user asked for a specific revision ("the design now uses X"), that is the starting edit.
   - If they only said "update" / "make this coherent", treat it as a coherence review: read the existing artifacts and check them against each other for contradictions, gaps, and duplication.

4. **Read and reconcile**
   - Read the artifact(s) the request touches and the change's other existing artifacts.
   - Draft the requested edit in the conversation, not in files. Work out exactly what it changes; step 5 owns every write. Then check every other existing artifact against the drafted edit - in ANY direction: an edit to a later artifact may require revising an earlier one, not only the other way around. Build order is a useful reading order, not a constraint on which artifacts may be revised.
   - Note everything that is now inconsistent, missing, or contradictory.
   - Propose revisions to files that already exist (`existingOutputPaths`). If an artifact has no existing output files and status `ready` or `blocked`, note it and point the user to `openspec instructions "<artifact-id>" --change "<name>" --json` for how to create them. Leave `skipped` artifacts untouched; do not treat them as missing or defer them to the continue workflow.
   - A glob artifact (e.g. `specs/**/*.md`) is marked `done` after at least one file matches, and the continue workflow only handles `ready` artifacts. When reconciliation identifies a missing file for a glob artifact whose `existingOutputPaths` is non-empty:
     1. Run `openspec instructions "<artifact-id>" --change "<name>" --json` and use its `instruction` and `template`. Treat `context` and `rules` as constraints; do not copy them into the file. If instructions report `skipped: true`, do not create the file. Read current dependency files from disk; if a required non-skipped dependency is missing, stop and ask the user to restore it first.
     2. Choose a concrete path inside `changeRoot` that matches `artifactPaths.<id>.outputPath` and does not already exist. Verify it remains inside `changeRoot` after resolving any symlinked parent directories. The glob `resolvedOutputPath` is not a valid target.
     3. Include the new file in step 5's proposed revisions and create it only after the user confirms.
     4. After confirmation, immediately before creation, refresh status and instructions. Verify the artifact is still in scope, not skipped, and partially populated; repeat the concrete-path checks above.
     5. Use a create operation that fails if the target already exists. If `instruction` delegates creation to another skill or command, invoke it only if it can honor the confirmed path and these guardrails; otherwise stop. If any check fails or the confirmed draft is no longer valid, stop and reconcile with the user rather than replacing existing content or choosing a different path.
   - If the change is already coherent, say so and propose no revisions.

5. **Confirm and apply, one artifact at a time**
   - This step performs every artifact write in this workflow; no earlier step edits an artifact.
   - Show each proposed revision and why - including the requested edit drafted in step 4. Write only after the user confirms.
   - If the user rejects a revision, do not write it - leave that artifact unchanged.
   - When a substantial rewrite is needed, get that artifact's rules and template first:
     ```bash
     openspec instructions "<artifact-id>" --change "<name>" --json
     ```

6. **Point to the next step (guidance only - NEVER act on it)**
   - Artifacts with empty `existingOutputPaths` and status `ready` or `blocked` -> run `openspec status --change "<name>" --json` for the next artifact and point the user to `openspec instructions "<artifact-id>" --change "<name>" --json` for how to create it.
   - Change already implemented (tasks checked off / already applied) -> the code may no longer match the revised plan; suggest `/openspec-apply-change` to carry the delta into code.
   - Everything done and implemented -> suggest `/openspec-archive-change`.

**Output**

After each invocation, show:
- Which artifacts were revised (and which proposed revisions were rejected)
- Any file created under a glob artifact that was already partially populated
- Anything deferred because it does not exist yet (artifacts with no files and status `ready` or `blocked`, never `skipped` artifacts)
- Where the change stands and the recommended next command

**Guardrails**
- Planning artifacts only - NEVER edit implementation code. If the revised plan implies code changes, stop and point to `/openspec-apply-change`.
- Use the artifact ids and paths reported by `openspec status`; never branch on hardcoded artifact names.
- Edit only the concrete files in `existingOutputPaths`, plus any confirmed concrete path allowed under a partly populated glob artifact (step 4); never write to a glob `resolvedOutputPath`.
- Do not advance the build frontier: if an artifact has empty `existingOutputPaths` and status `ready` or `blocked`, creating them is a separate step, outside this workflow. Leave `skipped` artifacts untouched. The only new-file scope is a confirmed concrete path under a glob artifact whose `existingOutputPaths` is non-empty.
- Confirm every edit with the user before writing.
- If the request changes the change's *intent* rather than refining it, ask for a distinct unused change name and recommend `openspec new change "<new-change-name>"` instead (the "Update vs. Start Fresh" heuristic).
