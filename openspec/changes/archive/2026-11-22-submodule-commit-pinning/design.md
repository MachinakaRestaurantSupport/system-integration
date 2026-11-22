# Design: サブモジュール参照のコミット指定統一とドキュメント生成の冪等化

## Context

従来のマルチリポジトリ運用では、`feature/<change-id>` 作業時に各サブシステムの `.gitmodules` の `branch` を変更して PR マージ後に `main` へ戻す二度手間が発生していた。そこで運用方針を「`.gitmodules` の `branch` 廃止＋確定コミット SHA 指定＋`system-integration` 先行 Merge commit 固定」へ統一するとともに、`feature/issue-3` レビュー中に顕在化した以下2点の技術的課題を解消する：

1. 各子リポジトリ（`system-integration` と 8 サブシステム）内の `.gitmodules`・`AGENTS.md`・`openspec/config.yaml`・`docs/system-design.md`・OpenSpec スキル定義に旧来の `branch` 切り替え手順が残存しており、全8サブシステムでは初回の `openspec/changes/init` も未アーカイブのまま残っている。
2. `system-integration/src/system_integration/doc_artifacts.py` がテストのたびに `_sync_to_subsystem_submodules()` で全8サブシステムの読み取り専用領域 `reference/system-integration/docs/images/` を直接上書きし、さらに `_normalize_html_for_hash()` が単独日付（`YYYY-MM-DD`）をマスクしていないため、別日実行だけで `sales_management` のキャプチャ差分とサブモジュール汚染が発生する。

## Goals / Non-Goals

- **Goals**:
  - 全8サブシステムの `.gitmodules` から `branch` 設定を削除し、`path` と `url` のみのコミット SHA 指定へ統一する。
  - `system-integration` および8サブシステムすべてのルール文書・設計書・OpenSpec スキルを新運用へ統一し、未アーカイブの `init` 変更を完了させる。
  - `doc_artifacts.py` からサブモジュール直接上書きを削除し、日付正規化を追加して冪等化する。
- **Non-Goals**:
  - 各サブシステムのビジネスロジック（FastAPI ルート・ストア・業務 UI）自体の仕様変更は行わない。

## Decisions

### 1. `.gitmodules` の純粋コミット指定化とルール統一（S05-01-01, S05-01-02）
- 各サブシステムの `.gitmodules` は以下の2項目のみに統一する：
  ```ini
  [submodule "reference/system-integration"]
  	path = reference/system-integration
  	url = https://github.com/MachinakaRestaurantSupport/system-integration.git
  ```
- 子リポジトリ内の `AGENTS.md`、`openspec/config.yaml`、`docs/system-design.md`、および `.agents/`・`.cline/`・`.github/`・`.hermes/` 配下の OpenSpec スキル記述から `git config -f .gitmodules ... branch ...` や `git submodule update --remote` を削除し、確定 `<commit-sha>` チェックアウトと `system-integration` 先行 Merge commit 手順に統一する。
- 全8サブシステムでは各自 `openspec:propose` → `apply` → `archive` でこれらを更新するとともに、未アーカイブの `openspec/changes/init` も `openspec archive init -y` でアーカイブ・仕様同期する。

### 2. `doc_artifacts.py` の冪等化とサブモジュール保護（S05-02-01）
- `_normalize_html_for_hash(html: str) -> str` について、既存の ISO タイムスタンプ置換（`YYYY-MM-DDTHH:MM:SS...`）に加えて単独の日付文字列 `r"\b\d{4}-\d{2}-\d{2}\b"`（または `r"\d{4}-\d{2}-\d{2}"`）を `"DATE-STATIC"` に置換し、`/ui/sales/daily`・`/ui/sales/monthly` 等の決済日表示が実行日に依存してハッシュ不一致を起こさないようにする。
  - 注意: すでに `TIMESTAMP-STATIC` に置換済みの箇所より後に単独日付正規化を適用すれば、タイムスタンプも日付も過不足なく正規化される。
- `capture_and_generate_docs()` から `_sync_to_subsystem_submodules(docs_images_dir, generated)` の呼び出しおよび関数本体を削除（廃止）する。サブシステム側の `reference/system-integration/` には git submodule（`git checkout <commit-sha>` / `git submodule update --init`）経由でのみ画像を反映し、テスト実行による読み取り専用領域の書き換えを根絶する。
- 単体・統合テストにて、`doc_artifacts._normalize_html_for_hash` が異なる `YYYY-MM-DD` を同一ハッシュへ正規化すること、および `capture_and_generate_docs` 実行後にサブシステムの `reference/system-integration` に未追跡・変更差分が生じないことを検証する。

## Risks / Trade-offs

- [リスク] `doc_artifacts.py` の `_normalize_html_for_hash` 変更後、既存の `.capture-hashes.json` ハッシュ値が変わるため初回実行時に一部 PNG/SVG が再生成される可能性がある → [対策] ハッシュ計算仕様更新サブタスク内で `FORCE_DOC_CAPTURE=1`（または再生成結果確認）と `docs/images/.capture-hashes.json` の同期を明示的に検証・コミットし、以後の別日再実行で差分ゼロになることを確認する。
- [リスク] 8サブシステムへの横断変更漏れ → [対策] OpenSpec タスクで全8サブシステムを個別にチェック管理し、全リポジトリ横断 `grep` で旧手順残存ゼロを検証する。
