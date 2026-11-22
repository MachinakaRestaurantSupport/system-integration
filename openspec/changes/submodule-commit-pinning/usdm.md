# USDM 要求仕様

# 【MachinakaRestaurantSupportTools】コンポーネント

## 要求

サブシステムにおける `reference/system-integration` サブモジュール管理をブランチ指定から確定コミット SHA 指定へ統一し、併せて E2E ドキュメント生成処理が読み取り専用サブモジュールや日付差分による作業ツリー汚染を起こさないこと。

### 理由

ブランチ切り替えによる `.gitmodules` の書き換えと PR マージ後の `main` 戻し作業を排除し、同時に別日の E2E テスト実行で不要な画像・サブモジュール差分が発生する問題を解消するため。

### 説明

全9リポジトリのワークフロー記述・`.gitmodules`・OpenSpec 管理状態、および `system-integration` のドキュメント生成モジュール `doc_artifacts.py` を整備する。

## 1.要件

### ＜R05＞サブモジュール参照のコミット指定統一とドキュメント自動生成の冪等化

#### 要求

サブモジュール参照を確定コミット SHA 指定に統一した上で、全リポジトリのルール・OpenSpec アーカイブ状態を揃え、E2E 画面キャプチャ処理を実行日付非依存かつサブモジュール非侵襲とすること。

##### 理由

マルチリポジトリ開発における PR マージ後の手戻りをなくし、テスト実行だけで未コミット差分が発生する状態を恒久的に防止するため。

##### 説明

`system-integration` の `create_merge_commit` 先行マージルールと合わせて運用を固定し、自動生成処理は `system-integration` 内部の成果物のみを対象とする。

#### 下位要求

##### ＜R05-01＞サブモジュール参照のコミット SHA 指定とワークフロールール統一

###### 要求

全8サブシステムの `.gitmodules` から `branch` 設定を完全に廃止し、各リポジトリのガイドライン・OpenSpec 運用状態を新方式へ統一すること。

- ■■■ **S05-01-01**: 全8サブシステムの `.gitmodules` から `branch` 設定を廃止して `path` と `url` のみとし、`reference/system-integration` は確定コミット SHA（gitlink）指定のみで管理すること。
- ■■■ **S05-01-02**: `system-integration` および全8サブシステムの `AGENTS.md`・`openspec/config.yaml`・`docs/system-design.md`・OpenSpec スキル定義を「submodule コミット SHA 指定＋`system-integration` 先行 Merge commit 固定」ルールへ統一し、各サブシステムの未アーカイブ `init` 変更をアーカイブ完了状態にすること。

##### ＜R05-02＞E2E ドキュメント生成の冪等化と読み取り専用サブモジュール保護

###### 要求

`system-integration` の E2E 自動キャプチャ処理が、実行日に依存したハッシュ不一致や他リポジトリのサブモジュールへのファイル上書きを行わないこと。

- ■■■ **S05-02-01**: `system-integration` の `doc_artifacts.py` から `_sync_to_subsystem_submodules` による読み取り専用サブモジュールへの直接ファイルコピーを廃止し、`_normalize_html_for_hash` で単独日付（`YYYY-MM-DD`）を正規化することで、実行日に依存せず作業ツリーを汚染しないこと。
