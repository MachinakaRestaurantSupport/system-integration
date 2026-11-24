# AGENTS.md — system-integration

MachinakaRestaurantSupportTools 全体システムの管理拠点リポジトリ。

## 仕様の正本（USDM Markdown）

- 全体: `usdm/machinaka_restaurant_support_tools/`
- サブシステム8件: `usdm/accounting_management/`, `usdm/dine_in_ordering/`, `usdm/guest_management/`, `usdm/menu_management/`, `usdm/order_management/`, `usdm/product_management/`, `usdm/sales_management/`, `usdm/takeout_ordering/`
- 記法: `../md2usdm/MANUAL.md`（完成例 `../md2usdm/examples/`）
- 全体システム設計: `docs/system-design.md`（連携ポイント I-1〜＝結合試験範囲、テスト戦略）

## OpenSpec（USDMスキーマ）運用ルール

本プロジェクトは `openspec/config.yaml` に定義された `usdm` スキーマ（`proposal` → `usdm` → `specs` → `design` → `tasks`）を使用する。OpenSpec アーティファクトおよび対話はすべて **日本語** で記述すること。

1. **Proposal (`proposal.md`)**:
   - `## Why` セクションは50文字以上1000文字以内で背景・目的を簡潔に記述する。
2. **USDM要求仕様 (`usdm.md`)**:
   - `affordd-prj/usdm-schema` のマークダウン形式定義（H1〜H6の固定見出し階層、偶数見出しの全角山括弧 `＜＞`、仕様項目の `- □□□ **Sxx-yy-zz**:` ラベル）を厳守する。
3. **Specs (`specs/**/spec.md`)**:
   - `openspec validate --strict` を通過させるため、各 `### Requirement:` 本文は500文字以内に収め、文中に必ず半角大文字の `SHALL` または `MUST`（例: `〜しなければならない（SHALL）。`）を含める。
   - `### Requirement:` の見出しには変更固有の連番（`R01` 等）を含めず恒久的な名前とし、直下の行に `**USDM**: R01-01` のメタデータ行として要求IDを記録する。
   - 各 `#### Scenario:` には必ず `**WHEN**`（または `**GIVEN**`）と `**THEN**` の両方を含める。
4. **Tasks (`tasks.md`)**:
   - 各チェックボックス項目（`- [ ] X.Y [Sxx-yy-zz] ...`）は **「1サブタスク ＝ 1コミット」** の粒度（変更ファイル数1〜5個程度、単独で検証・テストが通る最小単位）に分解する。
   - タスクは「サブシステムへの委譲指示」「サブシステム成果物の確認（実装〜単体試験）」「このリポジトリでの結合試験・総合試験」の3種に区別して書く。

## 実装・コミット規約（1サブタスク ＝ 1コミット）

OpenSpec の `apply` フェーズでは、以下のコミットルールを厳守すること。

1. **1サブタスク ＝ 1コミットの徹底**:
   - `tasks.md` のチェックボックス1項目（1サブタスク）を完了するごとに、単独で検証および既存・新規テストがすべてパスする状態（Green State）を確認する。
   - 該当サブタスクの変更ファイルおよび `tasks.md` のチェック更新（`- [ ]` → `- [x]`）を含めて **必ず1サブタスクにつき1コミット** を作成する（複数サブタスクを1コミットにまとめることは厳禁）。
2. **機械的変更と手動実装の完全分離**:
   - フォーマッタ実行、Linter自動修正、`sed` 等による一括置換、パッケージ追加などの「コマンド実行による機械的な変更」は、手書きのロジック変更や仕様記述とは別の独立した1サブタスク（＝1コミット）として切り出す。
3. **コミットメッセージと Git Trailers 書式**:
   - 1行目は `<type>(<scope>): <サブタスクの要約>` とする。
   - 本文に `Why:` と `What:` を記述し、末尾の Git Trailers に `Issue:` / `Task:` / `Verification:` / `Executed-Command:` を必ず記載する：

```text
<type>(<scope>): <サブタスクの要約>

Why: <このコミットの目的・背景>
What: <具体的な変更内容>

Issue: #<Issue番号（該当なしの場合は N/A）>
Task: <サブタスクの識別子とUSDM仕様ID（例: 1.1 [S01-03-02, S01-03-03]）>
Verification: <実行した確認コマンド（例: openspec validate <change-name> --strict）>
Executed-Command: <機械的変更時の実行コマンド全文、手動変更時は "manual">
```

## opsx フロー

1. **opsx:propose**: 最初にブランチ `feature/<change-id>` を作成してからアーティファクト着手
2. **opsx:apply**: `tasks.md` の各サブタスク（USDM・全体設計の更新、委譲指示、PR確認、結合・総合試験等）を「1サブタスク ＝ 1コミット」で順次実施・コミット
3. **opsx:archive**: 各サブシステムの単体試験および `openspec archive <change-id> -y` 完了を確認 → 結合試験・総合試験実施 → `usdm.md` のUSDM仕様ラベル更新（`□□□` → `■■■`）とコミット → `openspec validate <change-name> --strict` 確認 → アーカイブ → 必要に応じサブシステムの `reference/system-integration` 参照 SHA を確定コミットへ同期し、親ハブ PR（関連サブシステム PR 一覧＋`/files` 直リンク＋GitHub 横断 PR 検索 URL を先頭記載）および各サブシステム PR の作成を提案（push / PR 作成はユーザーの明示的指示後に実行）。結合・総合試験完了まで `main` にマージしない。マージ時は先に `system-integration` PR を必ず「Create a merge commit」（Squash 禁止）で `main` にマージし、続けて各サブシステム PR をそのまま `main` にマージする（マージ後の submodule 参照戻し作業は不要）。

## ルール

- `usdm/` 配下の USDM Markdown 編集後は `../.venv/bin/md2usdm usdm/<プロジェクト>` で Excel 再生成（`.xlsx` はコミット対象ではない）
- push / PR 作成はユーザーの明示的な指示後に実行し、PR 作成時・レビュー節目は必ず `https://github.com/pulls?q=is%3Apr+org%3AMachinakaRestaurantSupport+head%3Afeature%2F<change-id>` と `https://github.com/pulls?q=is%3Apr+is%3Aopen+org%3AMachinakaRestaurantSupport` で PR 残件を確認する（サブタスク単位のローカルコミットは上記「1サブタスク ＝ 1コミット」規約に従う）
