# Tasks: サブシステム間契約の改善（Issue #3）

## 1. system-integration 仕様・全体設計の更新

- [x] 1.1 [S04-01-01, S04-02-01, S04-02-02, S04-03-01, S04-03-02] `docs/system-design.md` に商品ID型統一・分割会計時の清掃遷移条件・正本価格参照（I-5拡張）の契約を追記し、`openspec validate contract-hardening --strict` を確認する
- [x] 1.2 [S04-01-01, S04-02-01, S04-02-02, S04-03-01, S04-03-02] 全体および対象4サブシステム（`product_management`, `accounting_management`, `dine_in_ordering`, `takeout_ordering`）の `usdm/` Markdown を更新し、`../.venv/bin/md2usdm` で Excel を再生成する

## 2. サブシステムへの実装委譲と成果物確認（単体試験完了まで）

- [x] 2.1 [S04-01-01] `product-management` へ商品ID文字列型統一（`str`、`prod-<hex>`）の実装・単体試験を委譲する（参照: `reference/system-integration/usdm/product_management/`、完了条件: `pytest` / `ruff check` 全パス）
- [x] 2.2 [S04-01-01] `product-management` の `feature/contract-hardening` 実装および単体試験完了を確認する
- [x] 2.3 [S04-02-01, S04-02-02] `accounting-management` へ席未払い注文残高チェック（`GET /tables/{table_id}/bill`）による分割会計時清掃遷移制御の実装・単体試験を委譲する（参照: `reference/system-integration/usdm/accounting_management/`、完了条件: `pytest` / `ruff check` 全パス）
- [x] 2.4 [S04-02-01, S04-02-02] `accounting-management` の `feature/contract-hardening` 実装および単体試験完了を確認する
- [x] 2.5 [S04-03-01] `dine-in-ordering` へ `ProductClient` 追加による注文時正本価格参照・持ち帰り可否検証の実装・単体試験を委譲する（参照: `reference/system-integration/usdm/dine_in_ordering/`、完了条件: `pytest` / `ruff check` 全パス）
- [ ] 2.6 [S04-03-01] `dine-in-ordering` の `feature/contract-hardening` 実装および単体試験完了を確認する
- [ ] 2.7 [S04-03-02] `takeout-ordering` へ `ProductClient` 追加による注文時正本価格参照・持ち帰り可否検証の実装・単体試験を委譲する（参照: `reference/system-integration/usdm/takeout_ordering/`、完了条件: `pytest` / `ruff check` 全パス）
- [ ] 2.8 [S04-03-02] `takeout-ordering` の `feature/contract-hardening` 実装および単体試験完了を確認する

## 3. 結合試験・総合試験（system-integration）

- [ ] 3.1 [S04-03-01, S04-03-02] `tests/conftest.py` を更新し、`dine_in` および `takeout` アプリへ `product` サービスの `FastAPIBridgeTransport` を注入する
- [ ] 3.2 [S04-01-01, S04-02-01, S04-02-02, S04-03-01, S04-03-02] `tests/integration/test_integration_points.py` を更新し、商品ID型統一・分割会計（2回目決済での席清掃遷移）・正本価格参照（改ざん単価無視と商品未存在エラー）の結合試験を追加・パスさせる
- [ ] 3.3 [S04-01-01, S04-02-01, S04-02-02, S04-03-01, S04-03-02] `tests/e2e/test_restaurant_e2e.py` を更新し、同一席での店内飲食＋店内発持ち帰りの分割会計E2Eシナリオを検証・パスさせる
- [ ] 3.4 [S04-01-01] 機械的整形（`../.venv/bin/ruff check --fix` / `ruff format`）を適用し、全テストとリンターのパスを確認する
