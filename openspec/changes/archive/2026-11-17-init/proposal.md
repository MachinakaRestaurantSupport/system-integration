# Proposal: MachinakaRestaurantSupportTools 初期システム設計とMVP実装

## Why

飲食店の店内注文・持ち帰り注文・席管理・商品/メニュー管理・注文かんばん・会計・売上集計の8つの業務ツールを連携させ、最小構成（MVP）として動作する初期実装を確立する必要がある。現在、全体設計と各サブシステムのUSDMはテンプレート状態であり、共通技術スタック（Python / FastAPI）と連携インターフェース（I-1〜I-6）を確定させ、全リポジトリで統一されたテスト可能な基盤を構築する。

## What Changes

- 全体アーキテクチャ・技術スタック（Python 3.12 + FastAPI + Pydantic + pytest + ruff）を `docs/system-design.md` に確定する。
- 全体および8サブシステムの初期要求仕様を `usdm/` 配下のUSDM Markdownに定義し、Excelを再生成する。
- サブシステム間のHTTP/REST連携インターフェース（I-1〜I-6）を設計し、各サブシステムへ初期実装（MVP＋単体試験）を委譲する。
- 全サブシステムの単体試験完了後、`system-integration` にて結合試験（I-1〜I-6）および総合試験（E2E）を実施する。

## Capabilities

### New Capabilities
- `system-architecture`: 全体システムと8サブシステムの共通技術基盤・データモデル・エラー規約を定義する。
- `subsystem-integration`: 連携ポイント I-1〜I-6 を介したサブシステム間連携フローとE2E業務シナリオを定義する。

### Modified Capabilities

## Impact

- `system-integration`: `docs/system-design.md`, `usdm/*/`, `tests/integration/`, `tests/e2e/`
- 8サブシステムリポジトリ: 各ツールの初期MVP実装（`src/`, `tests/`, `pyproject.toml`, `openspec/changes/init/`）
