# Proposal: サブシステム間契約の改善（ID型統一・分割会計・正本価格参照）

## Why

MVP v1.0 の結合試験および総合試験（Issue #3）を通じて、実運用に向けた3つの横断的契約課題が判明した。第一に `product-management` の商品IDのみ連番 `int` であり他サブシステムの `str` 型と不整合がある。第二に `accounting-management` が決済のたびに無条件で `request-cleaning` を呼ぶため、同一席の複数注文・分割会計の2回目決済で `guest-management` が `409 Conflict` を返す。第三に `dine-in-ordering` と `takeout-ordering` がクライアント指定の `unit_price` をそのまま信頼しており、商品マスタの正本価格と乖離するリスクがある。これらを解消し、実運用に耐える堅牢なサービス間契約を確立する。

## What Changes

- **ID型の統一**: `product-management` の商品IDを全サブシステム共通の `str` 型（例: `prod-<hex>`）へ統一し、関連契約を更新する。
- **同一席での複数注文・分割会計のサポート**: `accounting-management` が決済完了後に `order-management` の席未払い残高（`GET /tables/{table_id}/bill`）を確認し、未払い注文が0件になった時点でのみ `guest-management` へ `request-cleaning` を呼び出すよう変更する。
- **注文時の正本価格参照**: `dine-in-ordering` および `takeout-ordering` が注文作成時に `product-management`（`GET /products/{product_id}`）から正本価格・商品名・持ち帰り可否を参照し、単価を確定して `order-management` へ送信するよう変更する。
- **仕様・設計・結合試験の更新**: `docs/system-design.md`、関連 USDM、OpenSpec、および `tests/integration/`, `tests/e2e/` を更新して上記契約を検証する。

## Capabilities

### New Capabilities

### Modified Capabilities
- `subsystem-integration`: 商品ID型の統一、同一席分割会計時の清掃要求制御、および注文確定時の正本価格参照を追加する。

## Impact

- `system-integration`: `docs/system-design.md`, `usdm/`（全体および `product_management`, `accounting_management`, `dine_in_ordering`, `takeout_ordering`）, `tests/integration/`, `tests/e2e/`
- 影響サブシステム（4リポジトリ）: `product-management`, `accounting-management`, `dine-in-ordering`, `takeout-ordering`
- 参照のみ・契約確認対象: `menu-management`, `order-management`, `guest-management`, `sales-management`
