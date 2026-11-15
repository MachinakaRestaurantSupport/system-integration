↑ [【ProductManagement_R01】商品マスタ管理](./ProductManagement_R01.md "【ProductManagement_R01】")

# 【ProductManagement_R01.DM01】商品情報登録・更新・参照仕様

## 要求

商品の基本属性・栄養/アレルギー属性・提供条件（提供時間・オプション・持ち帰り可否）をAPI経由で登録・取得・一覧・更新できること。

### 理由

店内メニュー・持ち帰りメニュー双方で安全な商品情報（アレルゲンや持ち帰り可否）を保証するため。

### 説明

価格やカロリーは0以上の数値とし、不正値はHTTP 422で拒否する。

## 仕様

| 種別 | 内容 | 仕様番号 |
| --- | --- | --- |
| 仕様 | `POST /products` で分類・商品名・価格・アレルギー・カロリー・提供時間・オプション・持ち帰り可否を登録できる | 【ProductManagement_R01.DM01-01】 |
| 仕様 | `GET /products` および `GET /products/{product_id}` で商品一覧（持ち帰り可否フィルタ対応）と詳細を取得できる | 【ProductManagement_R01.DM01-02】 |
| 仕様 | `PUT /products/{product_id}` で商品情報を更新でき、存在しないIDには HTTP 404 を返す | 【ProductManagement_R01.DM01-03】 |
