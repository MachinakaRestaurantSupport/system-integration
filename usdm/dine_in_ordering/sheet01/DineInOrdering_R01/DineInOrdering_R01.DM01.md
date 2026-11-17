↑ [【DineInOrdering_R01】店内QR注文管理](./DineInOrdering_R01.md "【DineInOrdering_R01】")

# 【DineInOrdering_R01.DM01】席QR検証・カート・注文確定仕様

## 要求

席QRトークンの検証、店内/持ち帰り種別付き注文の受付、注文管理（I-1）への送信を提供すること。

### 理由

有効な着席セッションからの注文のみを許可し、店内からの追加持ち帰り注文にも柔軟に対応するため。

### 説明

不正または無効なQRトークンに対しては HTTP 404 または 403 を返す。

## 仕様

| 種別 | 内容 | 仕様番号 |
| --- | --- | --- |
| 仕様 | `POST /sessions` で席ID・QRトークンから店内注文セッションを開始・検証できる | 【DineInOrdering_R01.DM01-01】 |
| 仕様 | `POST /dine-in/orders` で店内飲食または店内発持ち帰り注文を受け付け、注文管理（I-1）へ連携できる | 【DineInOrdering_R01.DM01-02】 |
| 仕様 | `GET /dine-in/orders/{order_id}` で注文履歴・状況を参照できる | 【DineInOrdering_R01.DM01-03】 |
