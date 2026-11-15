↑ [1.要件](../index.md)

# 【MachinakaRestaurantSupportTools_R01】飲食店業務の統合支援基盤

## 要求

店内注文・持ち帰り注文・席管理・商品/メニュー管理・注文かんばん・会計・売上集計の8ツールが共通技術基盤上で連携し、飲食店業務を一貫して支援できること。

### 理由

各業務ツールが独立して開発・運用されつつ、データ連携（I-1〜I-6）によって店舗運営の省力化と正確性を実現するため。

### 説明

全体システム設計 `docs/system-design.md` に基づき、Python 3.12 / FastAPI / Pydantic v2 で構成する。

## 下位要求

- [01 共通基盤・サブシステム間連携要件](./MachinakaRestaurantSupportTools_R01.DM01.md "【MachinakaRestaurantSupportTools_R01.DM01】")
