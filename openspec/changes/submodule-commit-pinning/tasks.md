# Tasks: サブモジュール参照のコミット指定統一とドキュメント生成の冪等化

## 1. system-integration の仕様・ドキュメント・ルール整備

- [x] 1.1 [S05-01-02] `docs/system-design.md`（7章）と `AGENTS.md` を「submodule コミット SHA 指定＋`system-integration` 先行 Merge commit 固定＋親ハブPR目次・横断URL確認」ルールへ更新する
- [x] 1.2 [S05-01-02] `openspec/config.yaml` および `.agents/`・`.hermes/` 配下の OpenSpec スキル定義から旧 submodule ブランチ切り替え記述を排除し新ルールへ統一する

## 2. E2E ドキュメント生成の冪等化とサブモジュール保護（doc_artifacts.py）

- [x] 2.1 [S05-02-01] `src/system_integration/doc_artifacts.py` の `_sync_to_subsystem_submodules()` を廃止し、`_normalize_html_for_hash()` に単独日付（`YYYY-MM-DD`）の正規化を追加する
- [x] 2.2 [S05-02-01] 日付非依存のハッシュ正規化と読み取り専用サブモジュール非変更を検証するテストを追加し、必要に応じ更新された `.capture-hashes.json` 等を含め `pytest -q` と `ruff check .` がパスすることを確認する

## 3. 全8サブシステムへの展開（各サブシステム側 OpenSpec サイクル実施）

- [x] 3.1 [S05-01-01, S05-01-02] `product-management` で `feature/submodule-commit-pinning` を作成し、OpenSpec（`propose → apply → archive`）で `.gitmodules` の `branch` 行削除・`AGENTS.md`/`openspec/config.yaml`/スキル定義の更新・未アーカイブ `init` のアーカイブ・submodule 指定コミット同期を実施して単体試験パスを確認する
- [x] 3.2 [S05-01-01, S05-01-02] `menu-management` で同様に `.gitmodules` の `branch` 行削除・ルール統一・`init` アーカイブ・submodule 更新・単体試験パスを確認する
- [x] 3.3 [S05-01-01, S05-01-02] `guest-management` で同様に `.gitmodules` の `branch` 行削除・ルール統一・`init` アーカイブ・submodule 更新・単体試験パスを確認する
- [x] 3.4 [S05-01-01, S05-01-02] `dine-in-ordering` で同様に `.gitmodules` の `branch` 行削除・ルール統一・`init` アーカイブ・submodule 更新・単体試験パスを確認する
- [x] 3.5 [S05-01-01, S05-01-02] `takeout-ordering` で同様に `.gitmodules` の `branch` 行削除・ルール統一・`init` アーカイブ・submodule 更新・単体試験パスを確認する
- [x] 3.6 [S05-01-01, S05-01-02] `order-management` で同様に `.gitmodules` の `branch` 行削除・ルール統一・`init` アーカイブ・submodule 更新・単体試験パスを確認する
- [x] 3.7 [S05-01-01, S05-01-02] `accounting-management` で同様に `.gitmodules` の `branch` 行削除・ルール統一・`init` アーカイブ・submodule 更新・単体試験パスを確認する
- [ ] 3.8 [S05-01-01, S05-01-02] `sales-management` で同様に `.gitmodules` の `branch` 行削除・ルール統一・`init` アーカイブ・submodule 更新・単体試験パスを確認する

## 4. 横断検証と最終結合確認（system-integration）

- [ ] 4.1 [S05-01-01, S05-01-02, S05-02-01] 全9リポジトリの横断 `grep` で旧 submodule ブランチ切り替え記述・`.gitmodules` の `branch` 行・未アーカイブ change がゼロであることを確認し、`system-integration` の `pytest -q`・`ruff check .`・`ruff format --check` 実行後に全9リポジトリに未コミット差分が生じないことを検証する
