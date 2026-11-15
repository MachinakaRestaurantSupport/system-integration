# Design: MachinakaRestaurantSupportTools 初期システム設計（MVP）

## Context

`proposal.md` に基づき、8つのサブシステムを統一された Python 技術スタックで構築し、`I-1`〜`I-6` の連携ポイントで結合するための技術設計を定義する。

## Goals / Non-Goals

- **Goals**:
  - 全8サブシステムを Python 3.12 + FastAPI + Pydantic v2 + pytest + ruff で統一する。
  - 各サブシステムはインメモリリポジトリをデフォルトとし、外部DBなしに単体試験および結合試験が高速に動作するようにする。
  - サブシステム間通信（I-1〜I-6）は `httpx.Client` / `httpx.AsyncClient` を用いた REST/JSON クライアントとし、テスト時には `httpx.ASGITransport` を注入してインプロセス結合試験を行えるようにする。
- **Non-Goals**:
  - 本MVPでは本番永続化DB（PostgreSQL等）やフロントエンドSPAのビルド、実OAuthプロバイダへの外部ネットワーク通信は含まない（OAuthはプロバイダ種別＋トークン検証インターフェースのスタブ実装とする）。

## Decisions

### 1. 技術スタックとディレクトリ構成の統一
各サブシステムは以下の標準構成とする：
- パッケージ名: `src/<snake_case_name>/`（例: `src/accounting_management/`）
- 主要モジュール:
  - `main.py`: FastAPI `app` インスタンス、`create_app()` ファクトリ、`GET /health`
  - `models.py`: Pydantic v2 リクエスト/レスポンス/ドメインモデル
  - `store.py`: インメモリデータストア（テストごとのリセット機能付き）
  - `client.py`: 他サブシステム連携クライアント（必要な場合のみ、`httpx.Client` + `base_url` / `transport` 注入対応）
  - `router.py`（または `main.py` に統合）: 業務APIエンドポイント
- テスト: `tests/test_<module>.py`（`pytest` + `fastapi.testclient.TestClient`）
- 設定: `pyproject.toml`（`pytest`, `ruff` 設定）

### 2. 連携ポイント I-1〜I-6 の HTTP API 契約
- **I-1 (店内注文 → 注文管理)**: `POST /orders`（`source="dine_in"`, `table_id`, `session_id`, `items`）
- **I-2 (持ち帰り注文 → 注文管理)**: `POST /orders`（`source="takeout"`, `customer_id`, `pickup_at`, `items`）
- **I-3 (注文管理 → 会計管理)**: 会計管理 `POST /payments` が注文管理 `GET /orders/{order_id}` または `GET /tables/{table_id}/bill` を参照し決済完了、`POST /orders/{order_id}/mark-paid` 等で通知
- **I-4 (注文管理/会計 → 売上管理)**: `POST /sales/records`（`order_id`, `payment_id`, `channel`, `amount`, `recorded_at`）
- **I-5 (商品管理 → メニュー管理 → 注文ツール)**: 商品管理 `GET /products`、メニュー管理 `GET /menus/{channel}`（`channel="dine_in" | "takeout"`）
- **I-6 (顧客管理 ↔ 会計/注文)**: 顧客管理 `POST /tables/{table_id}/occupy`, `POST /tables/{table_id}/request-cleaning`, `POST /tables/{table_id}/release`, `GET /tables/{table_id}`, `POST /guests/{guest_id}/points`

### 3. テスト戦略
- **単体試験**: 各サブシステムリポジトリで `pytest` により全エンドポイントと境界値・異常系（404, 409, 422）を検証する。他サブシステム呼び出しは `httpx.MockTransport` または `ASGITransport` で検証する。
- **結合試験 (`system-integration/tests/integration/`)**: 8つの FastAPI アプリをインポートし、`httpx.ASGITransport` で相互接続して I-1〜I-6 を検証する。
- **総合試験 (`system-integration/tests/e2e/`)**: 商品登録→メニュー公開→来店受付→店内注文→調理かんばん→会計→席清掃・再利用→売上集計、および持ち帰り注文E2Eシナリオを検証する。

## Risks / Trade-offs

- [リスク] インメモリ実装のためプロセス再起動でデータが消える → [対策] MVPスコープとして明記し、Storeクラスを分離して将来のDB差し替えを容易にする。
- [リスク] サブシステム間のスキーマ不整合 → [対策] `system-integration` の結合試験で全8アプリを直接インポートして契約テストを実行する。
