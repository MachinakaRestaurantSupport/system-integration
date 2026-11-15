↑ [【GuestManagement_R01】来客・座席・再利用管理](./GuestManagement_R01.md "【GuestManagement_R01】")

# 【GuestManagement_R01.DM01】座席ステータス・来客受付・ポイント仕様

## 要求

座席の登録・状態遷移・セッション発行および会員ポイント管理をAPIとして提供すること。

### 理由

会計管理および店内注文からの状態連携（I-6）を整合性高く処理するため。

### 説明

不正な状態遷移（例: 着席中の席への二重受付）は HTTP 409 を返す。

## 仕様

| 種別 | 内容 | 仕様番号 |
| --- | --- | --- |
| 仕様 | `POST /tables` および `GET /tables/{table_id}` で座席登録・状態参照ができる | 【GuestManagement_R01.DM01-01】 |
| 仕様 | `POST /tables/{table_id}/occupy` で空席を着席中に遷移させ、来店セッションIDとQRトークンを発行する | 【GuestManagement_R01.DM01-02】 |
| 仕様 | `POST /tables/{table_id}/request-cleaning`（会計後）および `POST /tables/{table_id}/release`（清掃完了）で再利用可否を制御できる | 【GuestManagement_R01.DM01-03】 |
| 仕様 | `POST /guests` / `POST /guests/{guest_id}/points` で会員情報とポイントを管理できる | 【GuestManagement_R01.DM01-04】 |
