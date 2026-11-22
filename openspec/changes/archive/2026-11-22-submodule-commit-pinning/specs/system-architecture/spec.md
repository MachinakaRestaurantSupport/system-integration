# Spec: system-architecture

## Purpose

全8サブシステムの `reference/system-integration` サブモジュール参照をコミット SHA 指定に統一し、かつ E2E ドキュメント生成処理の冪等性と読み取り専用サブモジュールの保護を保証する。

## ADDED Requirements

### Requirement: サブモジュール参照のコミット指定とドキュメント生成の冪等性
**USDM**: R05-01
全サブシステムの `.gitmodules` は `branch` 設定を持たずコミット SHA（gitlink）のみで管理されなければならず（MUST）、`system-integration` の E2E ドキュメント生成は日付変動による不要な再描画および他リポジトリのサブモジュールへの直接上書きを行ってはならない（SHALL）。

#### Scenario: サブモジュール参照をコミット指定で同期しマージする
- **WHEN** サブシステムが確定コミット SHA で `reference/system-integration` を更新し、`system-integration` PR が Merge commit 方式で `main` にマージされる
- **THEN** サブシステムの `.gitmodules` 変更やマージ後の `main` 戻し作業なしで、各サブシステム PR をそのまま `main` へマージできる

#### Scenario: 別日に E2E ドキュメント生成テストを再実行する
- **WHEN** UI の実装変更がない状態で別日に `test_e2e_zzz_capture_portal_and_subsystem_screens` を実行する
- **THEN** `_normalize_html_for_hash` により日付文字列が正規化されて画像・遷移図は再生成されず、隣接サブシステムの `reference/system-integration/` にも一切の差分が発生しない
