↑ [【SalesManagement_R01】売上集計・レポート管理](./SalesManagement_R01.md "【SalesManagement_R01】")

# 【SalesManagement_R01.DM01】売上記録・日次月次年次集計仕様

## 要求

売上レコードの受信登録（I-4）および日次・月次・年次の売上集計APIを提供すること。

### 理由

同一注文の重複計上を防ぎつつ、正確な期間別・チャネル別売上レポートを出力するため。

### 説明

同一 `order_id` の重複登録は HTTP 409 または冪等に扱う。

## 仕様

| 種別 | 内容 | 仕様番号 |
| --- | --- | --- |
| 仕様 | `POST /sales/records` で売上レコード（注文ID・チャネル・金額・計上日時）を登録できる（I-4） | 【SalesManagement_R01.DM01-01】 |
| 仕様 | `GET /sales/summary/daily`, `GET /sales/summary/monthly`, `GET /sales/summary/yearly` で期間別集計を取得できる | 【SalesManagement_R01.DM01-02】 |
| 仕様 | 集計結果に総売上金額・注文件数・チャネル別内訳（`dine_in` / `takeout`）を含める | 【SalesManagement_R01.DM01-03】 |
