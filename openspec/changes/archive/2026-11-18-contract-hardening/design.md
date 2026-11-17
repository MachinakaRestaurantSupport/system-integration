# Design: サブシステム間契約の改善（Issue #3）

## Context

`init`（MVP v1.0）の結合試験・E2E試験により、以下3点の契約改善課題が特定された（Issue #3）。

1. `product-management` の商品 `id` が連番 `int` であり、他サービス（`str`）と不整合がある。
2. `accounting-management` が決済ごとに無条件で `guest-management` の `request-cleaning` を呼ぶため、同一席の複数注文・分割会計で2回目の決済が `409 Conflict` となる。
3. `dine-in-ordering` / `takeout-ordering` がクライアント送信の `unit_price` を信頼しており、商品マスタの正本価格と照合していない。

## Goals / Non-Goals

- **Goals**:
  - `product-management` の商品IDを `str` 型に統一し、全サービス間で型変換不要とする。
  - `accounting-management` が `order-management` の `GET /tables/{table_id}/bill` を確認し、未払い注文が0件になったときのみ `request-cleaning` を呼ぶようにする。
  - `dine-in-ordering` / `takeout-ordering` が `product-management` の `GET /products/{product_id}` から正本価格・商品名・持ち帰り可否を取得し、金額を確定する。
- **Non-Goals**:
  - 決済手段の分割（1注文を複数人で割り勘する機能）や、割引・クーポン計算の導入は本変更のスコープ外とする（対象は同一席に複数注文がある場合の注文単位決済＝分割会計）。

## Decisions

### 1. 商品ID型の統一（`product-management`）
- `product-management` の `Product.id` および `store` / `main.py` のパスパラメータ `product_id` を `int` から `str`（`f"prod-{uuid4().hex[:8]}"`）へ変更する。
- 他サブシステム（`menu-management`, `order-management`, `dine-in-ordering`, `takeout-ordering`）はすでに `str` として扱っているため変更不要。

### 2. 同一席・分割会計時の清掃要求制御（`accounting-management`）
- `accounting-management` の `OrderClient` に `get_table_bill(table_id: str) -> dict[str, Any]`（`GET /tables/{table_id}/bill`）を追加する。
- `POST /payments` 内で `mark_paid(order_id)` 実行後、`source == "dine_in" and table_id` の場合は `get_table_bill(str(table_id))` を呼び出し、`len(bill.get("order_ids", [])) == 0` の場合のみ `guest_client.request_cleaning(str(table_id))` を実行する。
- 単体試験ではモックで `order_ids` が残存するケース（`request_cleaning` 未呼出）と空になるケース（`request_cleaning` 呼出）の両方を検証する。

### 3. 注文確定時の正本価格参照（`dine-in-ordering`, `takeout-ordering`）
- `dine-in-ordering` と `takeout-ordering` に `ProductClient`（`GET /products/{product_id}`、環境変数 `PRODUCT_SERVICE_URL`、`create_app(..., product_client=...)` 注入対応）を追加する。
- リクエストスキーマ（`DineInOrderItem` / `TakeoutOrderItem`）は後方互換のため `product_name: str | None = None`、`unit_price: int | None = None` とオプショナルにするが、注文確定時は常に `product-management` から取得した `price` と `name` を採用して `order-management` に送信する。
- 存在しない `product_id` の場合は HTTP 404（または 422）、持ち帰り注文（`takeout-ordering` 全体、または `dine-in-ordering` で `is_takeout_from_table=True`）において `takeout_available is False` の商品が含まれる場合は HTTP 422 を返却する。
- `system-integration/tests/conftest.py` の結合試験ハーネスにて、`dine_in` および `takeout` アプリ生成時に `product` アプリへの `FastAPIBridgeTransport` を注入する。

## Risks / Trade-offs

- [リスク] `dine-in-ordering` / `takeout-ordering` の既存単体試験が `ProductClient` モックなしで `create_app()` を呼んでいる場合、テストが失敗する → [対策] 両サブシステムの既存単体試験にも `ProductClient` モック（または `ASGITransport`）を注入し、正常系・商品未存在・持ち帰り不可のケースを網羅する。
