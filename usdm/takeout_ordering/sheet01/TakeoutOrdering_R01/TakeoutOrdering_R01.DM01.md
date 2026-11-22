↑ [【TakeoutOrdering_R01】店外持ち帰り注文管理](./TakeoutOrdering_R01.md "【TakeoutOrdering_R01】")

# 【TakeoutOrdering_R01.DM01】SNS認証・受取予約・通知仕様

## 要求

SNSプロバイダログイン、受取予約時刻付き注文受付、状況確認および受取可能通知のAPIを提供すること。

### 理由

顧客が安心して事前注文し、適切なタイミングで来店・受取できるようにするため。

### 説明

対応プロバイダは `google`, `facebook`, `line` とし、未対応プロバイダは HTTP 422 で拒否する。

## 仕様

| 種別 | 内容 | 仕様番号 |
| --- | --- | --- |
| 仕様 | `POST /auth/login` で `google` / `facebook` / `line` プロバイダの認証セッションを発行できる | 【TakeoutOrdering_R01.DM01-01】 |
| 仕様 | `POST /takeout/orders` で受取予約時刻付き注文を受け付け、商品管理（`GET /products/{product_id}`）から正本価格・商品名・持ち帰り可否を検証・確定した上で注文管理（I-2）へ連携できる | 【TakeoutOrdering_R01.DM01-02】 |
| 仕様 | `GET /takeout/orders/{order_id}` および `POST /takeout/orders/{order_id}/notify-ready` で状況確認と受取可能通知を処理できる | 【TakeoutOrdering_R01.DM01-03】 |
