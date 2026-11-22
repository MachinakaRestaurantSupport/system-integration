# Proposal: サブモジュール参照のコミット指定統一と E2E ドキュメント生成の冪等化

## Why

これまでの運用では、各サブシステムで機能ブランチ作業のたびに `.gitmodules` の `branch` 設定を `feature/<change-id>` へ変更し PR マージ後に `main` へ戻す二度手間が発生し、一部サブシステムでは `.gitmodules` や未アーカイブの `init` 変更、`AGENTS.md`・スキル定義の不整合が残存していた。さらに、`doc_artifacts.py` が E2E テスト実行のたびに全サブシステムの読み取り専用サブモジュール `reference/system-integration/docs/images/` を直接上書きコピーし、単独の日付文字列（`YYYY-MM-DD`）をハッシュ正規化していないため別日実行時に未コミット差分が発生していた。これらを解消し、全9リポジトリを「submodule コミット SHA 指定方式」と冪等な E2E 画像生成・厳格な OpenSpec 運用へ統一する。

## What Changes

- **`.gitmodules` の `branch` 廃止とコミット SHA 指定化**: 全8サブシステムの `.gitmodules` から `branch` 行を削除し、`path` と `url` のみでコミット SHA（gitlink）管理へ統一する。
- **子リポジトリ 9 件のルール・設計・スキル統一と OpenSpec 整理**: `system-integration` および 8 サブシステムの `AGENTS.md`・`openspec/config.yaml`・`docs/system-design.md`・OpenSpec スキル定義を「submodule コミット SHA 指定＋`system-integration` 先行 Merge commit 固定」ルールへ更新し、各サブシステムに残存している `openspec/changes/init` をアーカイブする。
- **`doc_artifacts.py` の冪等化とサブモジュール保護**: `system-integration/src/system_integration/doc_artifacts.py` から `_sync_to_subsystem_submodules()` を廃止して読み取り専用サブモジュールへの直接書き込みを根絶し、`_normalize_html_for_hash()` で単独日付（`YYYY-MM-DD`）を正規化する。

## Capabilities

### New Capabilities

### Modified Capabilities
- `system-architecture`: サブモジュール参照のコミット SHA 指定および E2E ドキュメント生成の冪等性・読み取り専用保護を要件として追加する。

## Impact

- `system-integration`: `docs/system-design.md`, `AGENTS.md`, `openspec/config.yaml`, `.agents/`・`.hermes/` 配下の OpenSpec スキル定義, `src/system_integration/doc_artifacts.py`, 関連テスト（`tests/`）
- サブシステム全8リポジトリ（`product-management`, `menu-management`, `guest-management`, `dine-in-ordering`, `takeout-ordering`, `order-management`, `accounting-management`, `sales-management`）: `.gitmodules`, `AGENTS.md`, `openspec/config.yaml`, 各スキル定義（`.agents/`, `.cline/`, `.github/`, `.hermes/`）, `openspec/changes/init` のアーカイブおよび各リポジトリでの `submodule-commit-pinning` OpenSpec サイクル実施
