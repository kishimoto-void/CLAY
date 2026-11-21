# 手動アップロード案内

このフォルダは、CLAYリポジトリに手動で追加・置換するための公開文書セットです。GitHubへの変更・コミットは行っていません。

## 配置

| このパック内 | リポジトリ内の配置 | 操作 |
|---|---|---|
| `README.md` | `README.md` | 既存ルートREADMEを置換 |
| `START_HERE_LLM.md` | `START_HERE_LLM.md` | 新規追加 |
| `LICENSE_POLICY_JA.md` | `LICENSE_POLICY_JA.md` | 既存の方針メモを置換 |
| `docs/PROJECT_PHILOSOPHY.md` | `docs/PROJECT_PHILOSOPHY.md` | 新規追加 |
| `docs/COMMUNITY_GUIDE.md` | `docs/COMMUNITY_GUIDE.md` | 新規追加 |
| `docs/PROJECT_STATUS.md` | `docs/PROJECT_STATUS.md` | 新規追加 |
| `docs/FUTURE_DIRECTION.md` | `docs/FUTURE_DIRECTION.md` | 新規追加 |
| `docs/VALIDATION_GUIDE.md` | `docs/VALIDATION_GUIDE.md` | 新規追加 |
| `docs/PRIVACY_AND_DATA_HANDLING.md` | `docs/PRIVACY_AND_DATA_HANDLING.md` | 新規追加 |
| `docs/RESPONSIBLE_USE.md` | `docs/RESPONSIBLE_USE.md` | 新規追加 |
| `docs/VERSIONING.md` | `docs/VERSIONING.md` | 新規追加 |

## LICENSEについて

リポジトリ直下の `LICENSE` は拡張子なしの既存ファイルです。中身はPolyForm Noncommercial License 1.0.0です。このパックでは `LICENSE` を置換していません。

`LICENSE_POLICY_JA.md` は現行ライセンスと将来希望する条件の不一致を説明する検討メモです。これを `LICENSE` の代わりとして扱わないでください。正式なライセンスを選定・確認した後に、既存の `LICENSE` を差し替えるか判断してください。

## 推奨アップロード順

1. `docs/` フォルダと中の文書を追加する。
2. `START_HERE_LLM.md` を追加する。
3. `LICENSE_POLICY_JA.md` を置換する。
4. 最後にルート `README.md` を置換し、リンク切れがないか確認する。
5. GitHub上で各リンク、ファイル名、ライセンス表示を確認する。
