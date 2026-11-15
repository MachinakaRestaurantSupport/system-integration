# Tasks: MachinakaRestaurantSupportTools 初期システム設計とMVP実装

## 1. system-integration 仕様・全体設計の整備

- [x] 1.1 [S01-01-01] `openspec/schemas/usdm/` と `openspec/changes/init/` の OpenSpec 計画アーティファクトを登録し、`openspec validate init --strict` の通過を確認する
- [ ] 1.2 [S01-01-01] `docs/system-design.md` を更新し、技術スタック（Python / FastAPI）、アーキテクチャ構成、連携ポイント I-1〜I-6、テスト戦略を確定する
- [ ] 1.3 [S02-01-01, S02-01-02, S02-01-03] `usdm/machinaka_restaurant_support_tools/` およびマスタ・顧客系3サブシステム（`product_management`, `menu_management`, `guest_management`）の USDM Markdown を更新し、`../.venv/bin/python -m md2usdm` で Excel を再生成する
- [ ] 1.4 [S02-02-01, S02-02-02, S02-02-03, S02-02-04, S02-02-05] 注文・会計・売上系5サブシステム（`dine_in_ordering`, `takeout_ordering`, `order_management`, `accounting_management`, `sales_management`）の USDM Markdown を更新し、`../.venv/bin/python -m md2usdm` で Excel を再生成する

## 2. サブシステムへの実装委譲と成果物確認（単体試験完了まで）

- [ ] 2.1 [S02-01-01] `product-management` へ初期MVP実装（商品マスタCRUD・アレルギー/カロリー/持ち帰り可否・単体試験）を委譲し、完了とPR作成を確認する（参照: `reference/system-integration/usdm/product_management/`）
- [ ] 2.2 [S02-01-02] `menu-management` へ初期MVP実装（商品参照I-5・店内/持ち帰りメニュー作成公開・単体試験）を委譲し、完了とPR作成を確認する（参照: `reference/system-integration/usdm/menu_management/`）
- [ ] 2.3 [S02-01-03] `guest-management` へ初期MVP実装（座席状態/来客受付/清掃再利用/会員ポイントI-6・単体試験）を委譲し、完了とPR作成を確認する（参照: `reference/system-integration/usdm/guest_management/`）
- [ ] 2.4 [S02-02-03] `order-management` へ初期MVP実装（統合注文モデル・かんばん状態遷移・会計金額算出I-1/I-2/I-3・単体試験）を委譲し、完了とPR作成を確認する（参照: `reference/system-integration/usdm/order_management/`）
- [ ] 2.5 [S02-02-01] `dine-in-ordering` へ初期MVP実装（席QRトークン検証・メニュー参照I-5・注文確定I-1・店内持ち帰り・単体試験）を委譲し、完了とPR作成を確認する（参照: `reference/system-integration/usdm/dine_in_ordering/`）
- [ ] 2.6 [S02-02-02] `takeout-ordering` へ初期MVP実装（SNS認証スタブ・受取予約・状況確認・受取通知・注文確定I-2・単体試験）を委譲し、完了とPR作成を確認する（参照: `reference/system-integration/usdm/takeout_ordering/`）
- [ ] 2.7 [S02-02-04] `accounting-management` へ初期MVP実装（決済処理I-3・席状態更新I-6・売上通知I-4・単体試験）を委譲し、完了とPR作成を確認する（参照: `reference/system-integration/usdm/accounting_management/`）
- [ ] 2.8 [S02-02-05] `sales-management` へ初期MVP実装（売上レコード受信I-4・日次/月次/年次集計レポート・単体試験）を委譲し、完了とPR作成を確認する（参照: `reference/system-integration/usdm/sales_management/`）

## 3. 結合試験・総合試験（system-integration）

- [ ] 3.1 [S03-01-01, S03-01-02, S03-01-03] `pyproject.toml` と結合試験ハーネス（8サブシステムを `ASGITransport` で接続するフィクスチャ）を追加し、`pytest` 実行基盤を確認する
- [ ] 3.2 [S03-01-01, S03-01-02, S03-01-03] `tests/integration/test_integration_points.py` を実装し、連携ポイント I-1〜I-6 の結合試験をパスさせる
- [ ] 3.3 [S03-01-01, S03-01-02, S03-01-03] `tests/e2e/test_restaurant_e2e.py` を実装し、店内飲食E2Eおよび持ち帰りE2Eの総合試験をパスさせる
- [ ] 3.4 [S01-01-01] 機械的整形（`../.venv/bin/ruff check --fix` / `ruff format`）を適用し、全テストとリンターのパスを確認する
