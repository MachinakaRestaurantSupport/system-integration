↑ [【OrderManagement_R01】統合注文・かんばん管理](./OrderManagement_R01.md "【OrderManagement_R01】")

# 【OrderManagement_R01.DM01】統合注文受付・かんばん遷移・会計金額仕様

## 要求

店内（I-1）・持ち帰り（I-2）注文の登録、かんばんステータス更新、会計金額算出および支払済みマーク（I-3）を提供すること。

### 理由

注文の発生元によらず統一された業務フローと正確な請求金額計算を保証するため。

### 説明

不正なステータス逆転や存在しない注文IDへの操作は HTTP 409 / 404 を返す。

## 仕様

| 種別 | 内容 | 仕様番号 |
| --- | --- | --- |
| 仕様 | `POST /orders` で `dine_in` / `takeout` 注文を登録し、合計金額を自動算出する（I-1, I-2） | 【OrderManagement_R01.DM01-01】 |
| 仕様 | `PATCH /orders/{order_id}/status` でかんばんステータス（`received`→`preparing`→`ready`→`served`）を更新できる | 【OrderManagement_R01.DM01-02】 |
| 仕様 | `GET /orders/{order_id}`・`GET /tables/{table_id}/bill`・`POST /orders/{order_id}/mark-paid` で会計管理（I-3）と連携できる | 【OrderManagement_R01.DM01-03】 |
