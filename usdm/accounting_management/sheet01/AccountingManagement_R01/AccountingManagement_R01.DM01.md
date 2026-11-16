↑ [【AccountingManagement_R01】会計・決済・連携管理](./AccountingManagement_R01.md "【AccountingManagement_R01】")

# 【AccountingManagement_R01.DM01】決済処理・帳票・状態連携仕様

## 要求

注文に対する決済（現金/キャッシュレス）を実行し、お釣り計算・レシート情報生成・注文支払済み通知・席状態更新・売上連携を行うこと。

### 理由

二重会計を防ぎ、会計完了と同時に後続システム（顧客管理・売上管理）へ状態を伝播させるため。

### 説明

支払金額不足は HTTP 422、二重決済は HTTP 409 を返す。

## 仕様

| 種別 | 内容 | 仕様番号 |
| --- | --- | --- |
| 仕様 | `POST /payments` で注文金額に対する決済（現金・カード等）を完了し、レシート情報を返却できる（I-3） | 【AccountingManagement_R01.DM01-01】 |
| 仕様 | 会計完了時、注文管理の支払済み更新（I-3）、売上管理への計上（I-4）を実行し、店内注文かつ `GET /tables/{table_id}/bill` で未払い注文が0件となった場合のみ顧客管理の席清掃要求（I-6）を実行できる | 【AccountingManagement_R01.DM01-02】 |
| 仕様 | `GET /payments/{payment_id}` で会計履歴・帳票データを取得できる | 【AccountingManagement_R01.DM01-03】 |
