# CLAY Personalization

**A general-purpose framework for shaping an LLM interaction around the individual.**

> **Not optimized for everyone. Designed so anyone can personalize it.**

- **Current package:** v0.4.3 — experimental / public-preview stage
- **Initial target environment:** ChatGPT
- **Project direction:** general-purpose personalization, with optional community-built specialization
- **Maturity:** intentionally unfinished; v1.0 is a future maturity milestone, not a claim about the current package

[日本語](#日本語) · [English overview](#english-overview)

---

## 日本語

### CLAYとは

CLAY Personalizationは、LLMの知識量・推論能力・基礎性能そのものを高めることを目的としたシステムではありません。

利用者が自分の情報、目的、好み、作業方法を少しずつ与え、LLMとの対話の仕方や協働方法を自分に合う形へ形成していくための、汎用パーソナライゼーション基盤です。

CLAYという名前は粘土の比喩に由来します。システムが利用者に完成形を押し付けるのではなく、共通の土台を使って、利用者自身が必要な形を作っていきます。

**CLAYは、誰にとっても最適化済みのシステムではありません。誰にとっても、自分に合う形へ最適化していけることを目指すシステムです。**

### 何を目指すか

- 利用者ごとに異なる思考傾向、目的、情報の扱い方、対話の好みを尊重する。
- 一つの人格・職業・用途・回答形式を全員に強制しない。
- 必要に応じて、先回りの程度、提案の積極性、探索の幅、確認のタイミングを調整できるようにする。
- 利用者とLLMの相互理解を、対話・フィードバック・修正を通じて継続する。
- 特化した能力やワークフローは、共通基盤に詰め込まず、必要な場合に独立モジュールとして組み合わせられるようにする。
- 個人設定の形成・変更・削除に、利用者が主体的に関われるようにする。

### CLAYが目指していないこと

- LLM自体の知能、知識量、推論能力、モデル重みを増強すること。
- どのモデルでも必ず性能や正答率が向上すると保証すること。
- あらかじめ用意した一つの人格を全利用者に適用すること。
- 利用者の価値観や思考をCLAY側の理想に合わせて変えること。
- 利用者の明示的な確認なしに、永続的な個人設定を確定・保存すること。
- 宣言ファイルやモジュール仕様だけで、実際の権限付与・安全制御・外部操作が成立すると主張すること。

CLAYは「魔法のプロンプト」やモデル能力のアップグレードではありません。指示・文脈・適応方針を構造化し、利用可能なLLMの能力を利用者の目的に沿って活用しやすくするための枠組みです。効果はモデル、タスク、設定、利用環境に左右され、検証が必要です。

### 内部と外部の設計方針

- **内部：LLMが誤解しにくく、構造的に検証しやすいことを優先。** スキーマ、モジュール境界、優先順位、状態、検証条件、失敗条件を明示します。
- **外部：人間が理解・導入・調整しやすいことを優先。** 利用者に内部の複雑さをすべて理解させるのではなく、目的、使い方、変更方法、制約を分かりやすく説明します。

内部の複雑さは、無制限な複雑さを意味しません。各境界はテスト・検査できる必要があります。

### 基本構造

| 領域 | 役割 |
|---|---|
| Common Core | 共通の原則、事実性、主体性、制約、権限境界 |
| Personalization / Behavior Profile | 利用者が望む対話・協働の方向性 |
| Task Context | 今回の目的、条件、成果物、作業範囲 |
| Specialist Modules | 必要に応じた専門知識・ワークフロー・探索方法 |
| ChatGPT Adapter | 共通契約を現在のChatGPT利用環境向けに解釈する指針 |
| Host / Platform Boundary | 実際の機能、ツール、承認、権限、安全制御を担う環境側の境界 |

これらは役割の分離を示す設計モデルです。すべてが現行パッケージで自動実行されるわけではありません。

### 現在の対象範囲

現在の公開候補は、**ChatGPTを最初の対象環境として設計・検証する初期版**です。将来的な他LLMへの対応は方向性として想定していますが、現時点で他社モデルとの互換性や同等動作を保証しません。

### 現行パッケージでできること

- CLAYの共通原則、制御契約、モジュール境界を参照できる。
- Request Envelopeの検証、タスクオーバーレイの限定的な解決、ChatGPT向けコンテキストの準備を行う決定論的な参照実装を含む。
- Gamma / Deltaの参照コンポーネント、モジュールのマニフェスト／結果スキーマ、ローカル検証ツールを含む。
- 合成テストケースとローカルテストを通じて、宣言された構造や一部のヘルパー動作を検査できる。

### 現行パッケージに実装されていないこと

- ChatGPTや他のLLMを直接呼び出すAPIクライアント。
- 自動モジュール探索、ダウンロード、ロード、実行、サンドボックス。
- 永続的な個人データベース、完全な自動学習器、クロスセッションの個人設定保存。
- 実際のプラットフォーム権限や外部操作承認を強制する仕組み。
- 本番用のSafety Plane実行エンジン、意味的な真偽判定器、校正済み信頼度計算。
- すべてのLLMに対する動作保証、または実利用での改善保証。

テスト成功は、テストした環境における構造・ヘルパー動作の確認を意味します。ライブChatGPTの追従性、長期的な適応効果、本番セキュリティ、法令適合性を証明するものではありません。

### 使い始める

1. ZIPを展開するか、リポジトリを取得します。
2. ChatGPTにパッケージを渡し、まず `CHATGPT_LLM_SPEC.md` と `LLM_README.md` を読ませます。
3. パッケージの目的、現在実装されている機能、未実装の機能、利用上の制約を説明してもらいます。
4. 自分用に調整するときは `MODIFICATION_GUIDE.md` を使い、まず個人設定または振る舞い設定から小さく始めます。
5. 最初から個人情報を大量に入力する必要はありません。実際の用途に合わせ、必要な情報や好みを少しずつ追加・修正します。
6. 長期的な設定として残す場合は、内容を確認し、自分で保存・管理する方法を選びます。現在のパッケージ自体に永続保存機構はありません。

最初に使う依頼文の例：

```text
添付したCLAY Personalizationのパッケージを確認してください。
まずREADME.md、CHATGPT_LLM_SPEC.md、LLM_README.mdを読み、
このシステムの目的、現在実装されている機能、未実装の機能、
ChatGPTでの現実的な使い方を説明してください。
私が改造・パーソナライズを依頼した場合は、MODIFICATION_GUIDE.mdも参照してください。

CLAYがモデルの知能や推論能力を増強する、または自動的に
永続学習するとは扱わないでください。実装済みの機能と設計上の
構想を区別し、法令・プラットフォーム規則・安全上の制約を守ってください。
```

### 詳細資料とローカル確認

- `CHATGPT_LLM_SPEC.md` — ChatGPT向けLLM仕様書。
- `MODIFICATION_GUIDE.md` — 人間向けの改造手引書。個人設定・振る舞い・タスク・特化モジュール・Core変更の範囲と手順を説明します。
- `LLM_README.md` — LLMがパッケージを読む順序と作業手順。
- `CLAY_PERSONALIZATION.md` / `COMMON_CORE.md` / `SPEC.md` — 目的、共通原則、規範的な制御契約。
- `CHATGPT_ADAPTER.md` / `CONVERSATION_FLOW.md` — ChatGPTでの対話・適応方針。
- `MODULE_INTERFACE.md` / `schemas/` / `examples/` — モジュールの宣言形式と例。
- `SAFETY_PLANE_BOUNDARY.md` — 安全・権限境界と実装上の限界。
- `IMPLEMENTATION_STARTER.md` / `IMPLEMENTATION_VERIFICATION.md` — 現行の参照実装と確認結果。

ローカル確認の例（Python 3.10+、`requirements-dev.txt` の依存関係が必要）：

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -p 'test_runtime.py' -v
python tools/validate_control_topology.py
python tools/validate_modules.py examples/modules/code_specialist.example.json
```

これらは限定されたローカルチェックです。全機能・ライブChatGPT・本番環境の安全性を保証するものではありません。

### 法令・規範・安全について

CLAYおよび追加モジュールの利用・開発・配布では、利用者や運営者、利用地域、用途に適用される法令・規則、プラットフォームの利用規約・ポリシー、組織の規程、プライバシー、知的財産権、ライセンス条件を尊重してください。

- 違法行為や他者の権利侵害を目的とする利用を正当化しません。
- 個人情報・機密情報は、目的と必要性を確認し、本人の同意や適切な権限なく入力・共有しないでください。
- 他者のコード、文章、データ、モデル、モジュールを利用・再配布する場合は、適用されるライセンスや利用条件を確認してください。
- LLMに読み込ませる仕様書やモジュールは、上位のシステム指示、プラットフォームポリシー、実際の権限を上書きするものではありません。
- 法的判断が必要で適用法令や管轄が不明な場合は、断定せず、公式情報や資格を持つ専門家に確認してください。

この文書は法的助言ではなく、法令適合性を保証するものでもありません。

### コミュニティと今後

CLAYは一人で完成させることを前提としていません。共通基盤を保ちながら、利用者・開発者が用途別のモジュール、改善案、検証ケースを持ち寄れる構造を目指します。

特化モジュールを提案・公開する場合は、目的、対象範囲、対応するCLAYバージョン、必要な入力、権限、依存関係、テスト方法、実際の検証結果、失敗例、既知の制約を明記することを推奨します。未検証のものを検証済みと表示しないでください。

ただし、現時点ではコミュニティ審査、署名付き配布、信頼済みモジュールレジストリ、自動インストールなどは実装されていません。まずは公開後の反応や利用者の要望を見て、必要な規格や運用を段階的に整えていきます。

**v1.0は完成宣言ではなく、汎用基盤として一定の安定性・説明可能性・検証可能性を備えた成熟段階を目指す目標です。** 到達時期や完成は保証されず、利用者のフィードバックと検証を通じて育てていきます。

### ライセンスについて

この配布アーカイブには、現時点で明示的な `LICENSE` ファイルが含まれていません。GitHubで公開されていることだけで、第三者に利用・改変・再配布の許諾が与えられるわけではありません。公開前に、想定する利用・改変・再配布・貢献の範囲に合ったライセンスを選び、リポジトリに明記してください。

---

## English overview

CLAY Personalization is an experimental, general-purpose framework for shaping how an LLM interacts and collaborates with an individual. It does not increase the model's underlying intelligence, knowledge, or reasoning capability. It provides structures and guidance that users can shape through their own context, preferences, feedback, and optional specialist modules.

The default package is intentionally not personalized to its creator or to a predefined user archetype. It is designed to let different people form different configurations. The current package targets ChatGPT first; support for other LLM providers is a future direction, not a current compatibility claim.

Version 0.4.3 is an unfinished experimental preview. It contains declarative contracts, schemas, local validators, synthetic tests, and a deterministic adapter-preparation reference path. It does not include a live LLM client, automatic module loader, persistent personal-data store, autonomous learner, production permission enforcement, or live Safety Plane enforcement.

CLAY aims to grow through real use, feedback, and community contributions. A future v1.0 is a maturity goal, not a claim that the current release is complete. Users and contributors must respect applicable laws, platform rules, privacy, intellectual-property rights, and licenses. See the Japanese sections above for practical usage, scope, safety, and licensing notes.
