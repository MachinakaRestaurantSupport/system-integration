↑ [【MachinakaRestaurantSupportTools_R01】飲食店業務の統合支援基盤](./MachinakaRestaurantSupportTools_R01.md "【MachinakaRestaurantSupportTools_R01】")

# 【MachinakaRestaurantSupportTools_R01.DM01】共通基盤・サブシステム間連携要件

## 要求

全8サブシステムが共通API規約（`GET /health`、Pydantic検証）を満たし、連携ポイント I-1〜I-6 を介してE2E業務フローを完遂できること。

### 理由

独立したサブシステム間での契約不整合を防ぎ、結合試験および総合試験で品質を保証するため。

### 説明

テストは `httpx.ASGITransport` によるインプロセス連携で検証可能とする。

## 仕様

| 種別 | 内容 | 仕様番号 |
| --- | --- | --- |
| 仕様 | 全サブシステムが `GET /health` で HTTP 200 とサービス名を返却する | 【MachinakaRestaurantSupportTools_R01.DM01-01】 |
| 仕様 | I-1（店内注文→注文管理）および I-2（持ち帰り注文→注文管理）で注文が登録される | 【MachinakaRestaurantSupportTools_R01.DM01-02】 |
| 仕様 | I-3（注文管理↔会計管理）・I-4（売上管理）・I-5（商品/メニュー参照）・I-6（顧客/席管理）が連携してE2Eフローが完了する | 【MachinakaRestaurantSupportTools_R01.DM01-03】 |
