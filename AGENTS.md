# AGENTS.md — system-integration

MachinakaRestaurantSupportTools 全体システムの管理拠点リポジトリ。

## 仕様の正本（USDM Markdown）

- 全体: `usdm/machinaka_restaurant_support_tools/`
- サブシステム8件: `usdm/accounting_management/`, `usdm/dine_in_ordering/`, `usdm/guest_management/`, `usdm/menu_management/`, `usdm/order_management/`, `usdm/product_management/`, `usdm/sales_management/`, `usdm/takeout_ordering/`
- 記法: `../md2usdm/MANUAL.md`（完成例 `../md2usdm/examples/`）
- 全体システム設計: `docs/system-design.md`（連携ポイント I-1〜＝結合試験範囲、テスト戦略）

## opsx フロー

1. **opsx:propose**: 最初にブランチ `feature/<change-id>` を作成してからアーティファクト着手
2. **opsx:apply**: USDM・全体設計の更新とタスク作成（サブシステムへの委譲指示／PR 確認／結合・総合試験）
3. **opsx:archive**: 各サブシステムの単体試験状況を確認 → 結合試験・総合試験実施 → 完了で GitHub プルリクエスト作成。結合・総合試験完了まで main にマージしない。マージ時はファイル一覧の更新（各サブシステム側の submodule 参照コミット更新）

## ルール

- USDM Markdown 編集後は `../.venv/bin/md2usdm usdm/<プロジェクト>` で Excel 再生成（`.xlsx` はコミット対象ではない）
- エージェントワークフロー中に git commit を実行しない（commit / push / PR 作成はユーザーの明示的な指示後に実行）
