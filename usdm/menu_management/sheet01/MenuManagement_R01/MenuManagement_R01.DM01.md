↑ [【MenuManagement_R01】店内・持ち帰りメニュー管理](./MenuManagement_R01.md "【MenuManagement_R01】")

# 【MenuManagement_R01.DM01】メニュー作成・公開・参照仕様

## 要求

チャネル別（`dine_in` / `takeout`）のメニュー定義を作成・公開し、注文ツールから参照できること。

### 理由

店内注文と持ち帰り注文で異なるメニュー構成や公開状態を安全に制御するため。

### 説明

商品マスタ参照（I-5）により商品存在および持ち帰り可否を検証できる構成とする。

## 仕様

| 種別 | 内容 | 仕様番号 |
| --- | --- | --- |
| 仕様 | `POST /menus` でチャネル（`dine_in` / `takeout`）・カテゴリ・掲載商品リストを持つメニューを作成できる | 【MenuManagement_R01.DM01-01】 |
| 仕様 | `takeout` チャネルに持ち帰り不可商品が指定された場合、HTTP 422 または 400 で拒否する | 【MenuManagement_R01.DM01-02】 |
| 仕様 | `GET /menus/{channel}` で公開中のメニュー一覧（I-5）を取得できる | 【MenuManagement_R01.DM01-03】 |
