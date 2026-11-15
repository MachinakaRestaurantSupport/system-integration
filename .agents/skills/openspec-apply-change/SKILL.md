---
name: openspec-apply-change
description: Implement tasks from an OpenSpec change. Use when the user wants to start implementing, continue implementation, or work through tasks. Also use when the user says "openspec apply", "opsx apply", or "openspec implement".
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


Implement tasks from an OpenSpec change.

**Store selection:** If the user names a store (a store is a standalone OpenSpec repo registered on this machine) or the work lives in one, run `openspec store list --json` to discover registered store ids, then pass `--store <id>` on the commands that read or write specs and changes (`new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`, `schemas`, `view`). Once selected, treat `--store <id>` as sticky for the rest of the workflow. Every unscoped example of those commands below is shorthand: before running it, append the flag. For example, run `openspec status --change "<name>" --json --store "<id>"`, not the unscoped form shown below. Other commands do not take the flag. Hints printed by commands already carry the flag; keep it on follow-ups. Without a store, commands act on the nearest local `openspec/` root.

**Project check:** These steps expect a project that already uses OpenSpec. Before the first step that writes anything (`new change`, `archive`, `sync specs`, or authoring an artifact file), confirm the project has a root: run `openspec list --json` (with `--store <id>` when a store is selected, since the store is then the root) and read `root`. A root object means the project is set up. `"root": null` means it is not - there is no `openspec/` directory here, and a write such as `openspec new change` would create one as a side effect. The command also exits non-zero, which is that answer rather than a broken CLI, so read the JSON instead of retrying or working around it.

One `"root": null` is not about setup: when a `status` error message starts with `Declared in` or `Invalid store declaration in` and names this project's `openspec/config.yaml` (or `config.yml`), the project does use OpenSpec through a store it declares, which this machine cannot resolve (the store is not registered, or the `store:` line is malformed). Do not treat it as uninitialized and skip the branches below: stop before writing and show the user that error's `message` and `fix`.

Otherwise, with no root, what happens next depends on how this workflow was reached:

- **Auto-selected**: you chose this workflow yourself, without the user naming OpenSpec, naming this skill, or running its slash command. Stop using OpenSpec and answer the request normally, as you would with no OpenSpec installed. Do not ask them to set anything up and do not mention OpenSpec setup.
- **Explicit OpenSpec request**: the user named OpenSpec, named this skill, or ran its slash command. Stop before writing and ask how to proceed: set this project up (`openspec init`), target a store they already have (`--store <id>`), or continue without OpenSpec for this request. Wait for their answer.

In both branches, never create the root as a side effect: do not run `openspec init` until the user asks for it, do not hand-create `openspec/` files, and do not let a command create it.

**Input**: Optionally specify a change name (e.g., `/opsx-apply add-auth`). If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes and ask the user to select one

   Always announce: "Using change: <name>" and how to override (e.g., `/opsx-apply <other>`).

2. **Check status to understand the schema**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to understand:
   - `schemaName`: The workflow being used (e.g., "spec-driven")
   - `planningHome`, `changeRoot`, and `actionContext`: planning scope and edit constraints
   - Which artifact contains the tasks (typically "tasks" for spec-driven, check status for others)

3. **Get apply instructions**

   ```bash
   openspec instructions apply --change "<name>" --json
   ```

   This returns:
   - `contextFiles`: artifact ID -> array of concrete file paths (varies by schema - could be proposal/specs/design/tasks or spec/tests/implementation/docs)
   - Progress (total, complete, remaining)
   - Task list with status, source path, and source line
   - Dynamic instruction based on current state
   - Optional `context`: current required project instruction input from the selected root
   - Optional `operationGuidance`: current advisory guidance for apply
   - `missingArtifacts` (when present): required artifact ids with no output

   **Handle states:**
   - If `state: "blocked"`: show the message and pause implementation.
     - If `missingArtifacts` is non-empty: suggest completing the missing artifacts. Run `openspec status --change "<name>" --json`, select the next `ready` artifact (not `skipped` or `blocked`), and use `openspec instructions "<artifact-id>" --change "<name>" --json` for its rules and template. Keep the selected `--store <id>` on both commands.
     - Otherwise, follow the CLI instruction to create or repair the schema-configured tracking file from existing planning artifacts. Do not assume another artifact is ready or start implementation while blocked.
   - If `state: "all_done"`: report that all tracked tasks are complete and suggest review or verification as appropriate before archiving
   - Otherwise: proceed to implementation

   Treat `context` as a required prompt-level input. Read and consider it, and
   apply relevant project facts, conventions, and constraints while implementing.
   Treat `operationGuidance` as optional additive advice. Read and consider every
   entry, and follow entries that are applicable and compatible with the built-in
   workflow.

   Keep both fields separate from CLI-returned state, missing artifacts, tasks,
   progress, `contextFiles`, and the built-in `instruction`. They are not
   evidence of task completion, do not replace the built-in instruction, and do
   not permit bypassing a blocked state. If context conflicts with the built-in
   instruction, an explicit user choice, or a CLI-controlled value, report the
   conflict and preserve the controlling value. If guidance is inapplicable or
   conflicts with those controlling inputs, do not follow it and explain why.
   These are prompt-level behavior contracts, not enforceable checks.

4. **Read context files**

   Read every file path listed under `contextFiles` from the apply instructions output.
   The files depend on the schema being used:
   - **spec-driven**: proposal, specs, design, tasks
   - Other schemas: follow the contextFiles from CLI output

   Do not copy `context` or `operationGuidance` verbatim into implementation
   files or planning artifacts unless the user separately asks for that content.

5. **Show current progress**

   Display:
   - Schema being used
   - Progress: "N/M tasks complete"
   - Remaining tasks overview
   - Dynamic instruction from CLI

6. **Implement tasks (loop until done or blocked)**

   For each pending task:
   - Show which task is being worked on
   - Make the code changes required
   - Keep changes minimal and focused
   - Before editing, confirm the checkbox at the returned `sourcePath` and `line` still matches the task description; if it does not, rerun the apply instructions and use the refreshed location
   - Mark the task complete at its returned `sourcePath` and `line`: `- [ ]` → `- [x]`
   - Rerun the apply instructions and confirm that task is now done and progress changed
   - Continue to next task

   **Pause if:**
   - Task is unclear → ask for clarification
   - Implementation reveals a design issue → suggest updating artifacts
   - A task needs work beyond what the spec and tasks describe, or you are tempted to drop, narrow, defer, or accept exceptions to specified behavior to make it fit → surface the added scope and ask; do not absorb it silently
   - Error or blocker encountered → report and wait for guidance
   - User interrupts

7. **On completion or pause, show status**

   Display:
   - Tasks completed this session
   - Overall progress: "N/M tasks complete"
   - If all done: report that tracked tasks are complete and suggest review or verification as appropriate before archiving
   - If paused: explain why and wait for guidance

**Output During Implementation**

```
## Implementing: <change-name> (schema: <schema-name>)

Working on task 3/7: <task description>
[...implementation happening...]
✓ Task complete

Working on task 4/7: <task description>
[...implementation happening...]
✓ Task complete
```

**Output On Completion**

```
## Implementation Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 7/7 tasks complete ✓

### Completed This Session
- [x] Task 1
- [x] Task 2
...

All tracked tasks are complete. Review or verify the change as appropriate
before archiving. You can archive this change with `/opsx-archive`.
```

**Output On Pause (Issue Encountered)**

```
## Implementation Paused

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 4/7 tasks complete

### Issue Encountered
<description of the issue>

**Options:**
1. <option 1>
2. <option 2>
3. Other approach

What would you like to do?
```

**Guardrails**
- Keep going through tasks until done or blocked
- Always read context files before starting (from the apply instructions output)
- If task is ambiguous, pause and ask before implementing
- If implementation reveals issues, pause and suggest artifact updates
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task
- Pause on errors, blockers, or unclear requirements - don't guess
- When a task needs work beyond what the spec describes, surface the added scope and pause - never silently narrow, defer, or simplify away specified behavior
- Only mark a task `- [x]` when its specified behavior is fully implemented, not when it is partially done or deferred
- Use contextFiles from CLI output, don't assume specific file names
- Use each task's sourcePath and line to update its exact checkbox
- Do not use context or operation guidance as proof that a task is complete
- Apply relevant project context; report conflicts with controlling workflow inputs
- Consider every guidance entry; explain any inapplicable or conflicting advice
- Do not copy runtime context or operation guidance into implementation files or planning artifacts
- Preserve CLI-controlled blocked/ready/all-done behavior and completion criteria

**Fluid Workflow Integration**

This skill supports the "actions on a change" model:

- **Can be invoked anytime**: Before all artifacts are done (if tasks exist), after partial implementation, interleaved with other actions
- **Allows artifact updates**: If implementation reveals design issues, suggest updating artifacts - not phase-locked, work fluidly
