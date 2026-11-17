↑ [1.要件](../index.md)

# 【OrderManagement_R01】統合注文・かんばん管理

## 要求

店内の席ごとおよび店外持ち帰り注文をかんばんで一元管理し、受付・調理・お届けの進行と会計金額の連携を行えること。

### 理由

キッチンとホールの情報共有を統一し、注文の抜け漏れや会計金額の計算誤りをなくすため。

### 説明

状態遷移は `received` → `preparing` → `ready` → `served`（または `completed`）とする。

## 下位要求

- [01 統合注文受付・かんばん遷移・会計金額仕様](./OrderManagement_R01.DM01.md "【OrderManagement_R01.DM01】")
