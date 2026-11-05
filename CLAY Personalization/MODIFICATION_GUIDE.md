# CLAY Personalization — 改造手引書

**手引書バージョン:** 0.1  
**対象パッケージ:** CLAY Personalization v0.4.3  
**対象環境:** まずはChatGPT  
**文書の目的:** 利用者がCLAYを自分の用途に合わせて調整・拡張するための案内  
**位置づけ:** 人間向けガイド。実行可能な機能や権限を新たに付与する仕様ではありません。

> **CLAYは、完成された人格や用途を配布するものではありません。共通の土台を使い、利用者自身が必要な形を作っていくための基盤です。**

---

## 1. はじめに — CLAYで何を改造できるのか

CLAY Personalizationは、LLMの知識量・推論能力・モデル自体の性能を直接増やすシステムではありません。利用者の目的、好み、情報の扱い方、作業方法に合わせて、LLMとの対話や協働の形を調整するための汎用基盤です。

CLAYの改造は、必ずしもプログラムを書くことではありません。最初は自然文で自分の希望を伝えるだけでも構いません。必要になったときに、設定、振る舞いの定義、タスク別モジュール、実装へと段階的に進められます。

### まず知っておいてほしいこと

- CLAYの標準状態は、特定の開発者や職業、人格、思想に最適化されていません。
- 個人設定は利用者自身が選び、追加し、修正し、削除します。
- 一時的な依頼と、長期的に使う個人設定は分けてください。
- 専門用途の機能は、可能な限り共通Coreではなく独立モジュールとして扱います。
- 現行v0.4.3は実験的な基盤です。すべての構想が実装済みという意味ではありません。
- 仕様書・プロンプト・モジュール宣言だけで、ChatGPTに新しいツール権限や永続メモリ、自動実行機能が生まれるわけではありません。

## 2. 改造する場所を選ぶ

最初に「何を変えたいのか」を見極めます。目的を満たすために、最も変更範囲の小さい場所から選ぶのが基本です。

| 領域 | 変更するもの | 例えば | 推奨度 |
|---|---|---|---|
| A. 個人設定 | 自分の情報・好み・目的 | 詳細さ、専門知識、関心、回答形式 | 最初に試す |
| B. 振る舞い設定 | LLMとの協働方法 | 先回り、探索幅、質問頻度、提案の仕方 | 積極的に調整 |
| C. タスク設定 | 今回の作業だけの条件 | 今日は価格重視、今回は厳密な検証 | 必要なとき |
| D. 特化モジュール | 用途固有の手順・能力契約 | 買い物支援、研究補助、コードレビュー | 拡張時 |
| E. Core | 全利用者・全モジュールに関わる共通仕様 | 共通スキーマ、制御境界、共通ルール | 原則として最後 |

**判断の目安:** 「自分に合わせたい」ならAまたはB、「今回だけ条件を変えたい」ならC、「専門的な仕事の手順を追加したい」ならD、「複数のモジュールや全体の共通契約を変えないと実現できない」場合に限ってEを検討します。

## 3. A — 個人設定を作る

個人設定では、自分についてLLMに知っておいてほしい情報と、回答に反映してほしい希望を伝えます。最初から詳しいプロフィールを作る必要はありません。

### 例：買い物の好みを追加する

次のように自然文で依頼できます。

```text
買い物を相談するときは、価格だけでなく耐久性、使いやすさ、
維持費、価格に対する満足度も比較してほしい。

候補は定番品だけに限定せず、条件に合う知らない商品も探してほしい。
ただし、予算を勝手に決めず、価格帯が分かれる場合は確認してほしい。

この内容を個人設定の候補として整理してください。
まだ保存・確定せず、私が確認できる形で提示してください。
```

LLMには、少なくとも次の区別をさせてください。

- **明示した好み:** 利用者が直接伝えた内容
- **推測:** 対話から推定したが、本人の確認が取れていない内容
- **タスク限定:** 今回だけ適用する条件
- **未設定:** 情報がない状態。否定や拒否と同じ意味にしない

長期的な設定として使う場合は、内容を確認してから自分で保存・管理してください。現行v0.4.3自体には、個人設定を自動で永続保存する機能はありません。

## 4. B — LLMの振る舞いを調整する

個人情報と、LLMにどう振る舞ってほしいかは別の設定です。職業や趣味を登録しなくても、対話の進め方だけを調整できます。

調整できる考え方の例:

- **先回りの深さ:** 次に必要になりそうなことをどこまで予測するか
- **自発性:** どの程度、自分から提案・確認・探索するか
- **探索幅:** 既知の候補だけでなく、新しい候補をどこまで探すか
- **確認のタイミング:** どの段階でユーザーに尋ねるか
- **決定の境界:** 提案は任せても、最終決定は利用者に残す領域
- **説明の密度:** 結論中心か、根拠や過程の説明も含めるか

これらは現行仕様で使うための概念的な調整軸です。v0.4.3に、すべての軸を自動調整する完成済みコントローラーが含まれているわけではありません。

### 例：先回りをタスクごとに変える

```text
私は、先回りの強さをすべての会話で同じにしたくありません。

・飲食店や買い物の探索では、候補や未知の選択肢を積極的に探してほしい。
・開発や設計では、将来の拡張性、競合、破壊テストまで先回りして考えてほしい。
・雑談では、話題を広げてもよいが、勝手に課題や計画に変えないでほしい。
・医療、金銭、外部への申込みなど影響が大きい判断では、選択肢とリスクを整理し、決定前に確認してほしい。

この希望を、個人の振る舞い設定とタスク別の適用条件に分けて整理してください。
```

### 設定メモの例（説明用）

次のYAML風の記述は、希望を整理するための**説明用メモ**です。現行v0.4.3のJSON Schemaや実行可能な設定ファイルではありません。

```yaml
behavior_preferences:
  discovery_tasks:
    anticipation: high
    exploration_width: wide
    ask_before_commitment: true
  casual_chat:
    initiative: moderate
    avoid_unsolicited_project_planning: true
  high_impact_decisions:
    explain_options_and_risks: true
    final_decision_owner: user
```

LLMにこのメモを渡す場合は「これは希望の整理案であり、実装済みの制御値として扱わない」と伝えてください。実際の設定形式へ変換する場合は、対象ファイルとスキーマを確認してから行います。

## 5. C — タスク設定を使う

長期的な個人設定を変えずに、その回の作業だけを切り替える方法です。

### 例：同じ人でも目的によって変える

**買い物をするとき**

```text
今回は予算を最優先にしつつ、最低限の耐久性は確保してください。
候補は3〜5件。価格・長所・短所・確認できていない点を比較してください。
```

**設計レビューをするとき**

```text
今回は厳密性を優先してください。
仕様の矛盾、入力境界、失敗時の挙動、互換性、悪用可能性を確認し、
実施したテストと未実施のテストを分けて報告してください。
```

これらはタスク限定の指示です。本人が明示的に希望しない限り、永続的な個人設定に自動変換しないでください。

## 6. D — 特化モジュールを作る

同じ用途を何度も行う、あるいは専門的な手順をまとめたい場合は、特化モジュールを検討できます。

例:

- 買い物・商品比較
- 飲食店・旅行先の探索
- プログラミング・コードレビュー
- 調査・資料整理
- 学習・教材作成
- 趣味の記録や計画

モジュールを作るときは、まず目的を自然文で説明し、次に入力・出力・対象外・検証方法を整理します。

### 6.1 モジュール設計を依頼する例

```text
CLAY v0.4.3のCoreは変更せず、買い物支援の特化モジュールを設計してください。

目的:
価格だけでなく、耐久性、使い勝手、維持費、条件との適合性を比較し、
利用者が知らない候補も探索できるようにする。

必須事項:
・ユーザーの予算や購入意思を勝手に決めない。
・価格、在庫、仕様など変動する情報は、確認した情報と未確認情報を区別する。
・購入や決済などの外部操作は実行しない。
・個人情報は必要最小限にし、既定ではタスク内に限定する。
・モジュールの対象外と失敗条件を定義する。
・検証ケースと既知の制約を付ける。

まず設計案を出し、既存のModule Interfaceとの互換性を確認してください。
宣言ファイルだけで実行機能が追加されたとは扱わないでください。
```

### 6.2 モジュールの基本構成例

コミュニティで共有する場合の推奨構成例です。これは将来の整理にも使える**提案ディレクトリ構成**であり、現行パッケージに自動ローダーがあるという意味ではありません。

```text
shopping-assistant/
├── README.md              # 人間向け説明・導入方法
├── MODULE.md              # 振る舞い・手順・制約
├── manifest.json          # CLAY module manifest
├── examples/              # 入出力例
└── tests/                 # 検証ケース・結果
```

- `README.md`: 何のためのモジュールか、どう使うかを説明します。
- `MODULE.md`: LLMに与える手順、判断基準、出力形式、例外を説明します。
- `manifest.json`: 識別子、能力、入力・出力、依存関係、権限境界などを宣言します。
- `examples/`: 想定される使い方を示します。
- `tests/`: 期待する挙動、失敗例、境界条件、検証記録を残します。

### 6.3 manifestの例

以下は現行の `schemas/module_manifest.schema.json` に合わせた、買い物支援モジュールの**宣言例**です。スキーマとローカル検証ツールに適合する形を示しますが、これだけでモジュールの実行機能や商品検索機能が追加されるわけではありません。

```json
{
  "schema_version": "clay/module-manifest/v1",
  "module_id": "shopping.assistant",
  "name": "Shopping Assistant Example",
  "module_version": "0.1.0",
  "kind": "domain_specialist",
  "purpose": "Compare product candidates against user-provided needs, budget, durability, usability, and maintenance considerations.",
  "capabilities": [
    {
      "capability_id": "shopping.compare",
      "description": "Compare supplied or actually retrieved product candidates against explicit user criteria."
    },
    {
      "capability_id": "shopping.discover",
      "description": "Suggest additional candidate categories or search directions without claiming retrieval was performed."
    }
  ],
  "out_of_scope": [
    "Making a purchase or payment",
    "Claiming current prices or stock without a current source",
    "Granting itself external tool permissions",
    "Persistently storing personal information"
  ],
  "implementation_modes": [
    "single_model",
    "external_tool",
    "human_in_loop",
    "hybrid"
  ],
  "inputs": [
    {
      "name": "user_goal",
      "required": true,
      "description": "The item or outcome the user is considering."
    },
    {
      "name": "constraints",
      "required": false,
      "description": "Budget, location, compatibility, size, timing, or other user-stated constraints."
    },
    {
      "name": "candidate_products",
      "required": false,
      "description": "Product candidates actually supplied by the user or retrieved through an available source."
    }
  ],
  "outputs": [
    {
      "name": "comparison",
      "description": "A comparison of candidates against stated criteria, with missing information identified."
    },
    {
      "name": "recommendation_options",
      "description": "A bounded set of suitable options and trade-offs; the user retains the purchase decision."
    },
    {
      "name": "verification_record",
      "description": "Sources checked, details not verified, and any execution or retrieval limitations."
    }
  ],
  "dependencies": [],
  "clay_core_range": "0.4.x",
  "risk_class": "moderate",
  "verification_requirements": [
    "Separate user-stated constraints from inferred preferences.",
    "Do not state current price, availability, or specifications without a current source.",
    "Do not claim a search or purchase occurred unless its result is observed.",
    "Keep purchase and payment decisions with the user."
  ],
  "behavior_profile": {
    "separate_from_capability": true,
    "supported_controls": [
      "verbosity",
      "format",
      "initiative",
      "question_frequency",
      "collaboration_style"
    ],
    "may_override_common_core": false
  },
  "authority": {
    "may_grant_permissions": false,
    "may_modify_common_core": false,
    "may_disable_safety_plane": false,
    "external_action_default": "forbidden_without_host_approval"
  },
  "data_handling": {
    "default_scope": "task_only",
    "persistent_personal_data": false
  },
  "failure_contract": {
    "declares_typed_blockers": true,
    "retry_policy": "bounded_host_policy",
    "partial_results_supported": true
  },
  "notes": [
    "Illustrative manifest for the CLAY v0.4.3 module contract.",
    "The manifest is declarative. The current package does not automatically discover, load, or execute this module."
  ]
}
```

### 6.4 モジュール作成後に確認すること

- 対象Coreバージョンと互換性が明示されているか。
- 対象範囲と対象外が具体的か。
- 入力・出力が明確か。
- 個人設定、専門能力、タスク条件、権限が混同されていないか。
- 必要な個人情報が最小限か。
- 失敗時に、できないこと・不足情報・未検証事項を返せるか。
- 期待ケースだけでなく、矛盾・空欄・極端値・誤入力なども検証したか。
- 実際に実行したテストと、設計上の予定を区別しているか。

現行パッケージにはmanifest/resultのスキーマとローカル検証ツールがありますが、自動モジュール探索・ダウンロード・インストール・ロード・実行・サンドボックスはありません。検証に合格したmanifestは、宣言形式が適合したことを示すものであり、モジュールの動作や安全性を証明するものではありません。

## 7. E — Coreそのものを変更する

Coreは多くの利用者・モジュールに影響する共通部分です。個人設定や外部モジュールで実現できるなら、Coreは変更しないでください。

### v0.4.3の基準点

v0.4.3は、汎用性と具体性の均衡を保つための**Generic Core Design Freeze（汎用Coreの設計基準点）**として扱うことを推奨します。

- v0.4.3の基準パッケージを直接上書きしない。
- Core変更が必要なら、コピーまたはforkで別案を作る。
- 変更理由、影響するファイル、維持する不変条件、互換性、移行方法を記録する。
- スキーマや権限の意味を変える場合は、互換性を保てるか検証する。
- Safety Plane、実際のホスト権限、法令・プラットフォーム規則を弱める変更は、個人設定やモジュールの要望として受け入れない。
- 既存の検証を再実行し、回帰・破壊テストを追加する。

### Core変更を依頼する例

```text
この変更は個人設定や外部モジュールでは実現できず、Core変更が必要かを先に判定してください。

必要な場合は、v0.4.3の基準パッケージを直接上書きせず、別ブランチ相当の変更案を作ってください。

次を提示してください。
1. Core変更が必要な理由
2. 変更するファイル・スキーマ・契約
3. 既存利用者とモジュールへの影響
4. 維持する不変条件と安全・権限境界
5. 互換性・移行・ロールバック方針
6. 追加する正常系・異常系・破壊テスト
7. 実際に行った検証と未検証事項

判断できない点は推測で確定せず、既存Coreを維持した代替案も提示してください。
```

## 8. LLMに改造を頼むときの共通テンプレート

次のテンプレートを使うと、LLMが変更範囲を取り違えにくくなります。

```text
CLAY Personalizationを次の目的に合わせて調整したいです。

【目的】
ここに実現したいことを書く。

【対象】
個人設定 / 振る舞い設定 / タスク設定 / 特化モジュール / Core変更 / 未定

【希望する動作】
具体的にどう振る舞ってほしいかを書く。

【変えたくないこと】
維持したい設定、既存仕様、権限境界などを書く。

【成果物】
説明、設定案、Markdown、manifest、コード、更新済みZIPなど必要なものを書く。

まず要求を分類し、変更範囲が最小になる案を提案してください。
既存ファイルやスキーマを確認し、仕様に合わない形式を勝手に追加しないでください。
実装・編集・テストを行った場合は、実施内容と結果を区別して報告してください。
```

## 9. 検証と公開 — 「作った」と「動いた」を分ける

改造後は、成果物の状態を明確にします。次の段階は説明用の目安であり、公式認証制度ではありません。

| 状態 | 意味 |
|---|---|
| Draft | 設計案・草案。検証は未実施または限定的 |
| Structurally Validated | スキーマや静的構造の検証に合格 |
| Local Tests Passed | 明記されたローカルテストが合格 |
| Live ChatGPT Observed | 対象のChatGPT環境で指定テストを実施し、結果を記録 |
| Community Reviewed | 第三者レビューを受け、指摘と対応を記録 |

一つの状態に達しても、他の性質まで保証されるわけではありません。例えば、manifestのスキーマ検証は実行動作の証明ではなく、少数の会話テストは長期的な改善の証明ではありません。

### 公開前チェックリスト

- [ ] モジュール名、作者または公開主体、バージョンが明記されている。
- [ ] 目的・対象範囲・対象外が明記されている。
- [ ] 対応するCLAY Coreの範囲が明記されている。
- [ ] 必要な入力・個人情報・外部ツールが明記されている。
- [ ] 権限を自己付与しないこと、CoreやSafety Planeを上書きしないことが明記されている。
- [ ] テスト方法、実施結果、失敗例、既知の制約が記録されている。
- [ ] 未検証部分を検証済みと表現していない。
- [ ] 第三者のコード・データ・文章・モデル等のライセンスと再配布条件を確認している。
- [ ] 個人情報、認証情報、APIキー、秘密情報が混入していない。
- [ ] 配布に適用するライセンスが明記されている。

## 10. 法令・規範・安全・プライバシー

改造やモジュール公開では、利用者・開発者・配布者・利用地域・用途に適用される法令、プラットフォームの利用規約・ポリシー、組織の規程、プライバシー、知的財産権、ライセンス条件を尊重してください。

- 違法行為、他者の権利侵害、プラットフォーム規則の回避を目的とする改造を正当化しません。
- 個人情報・機密情報・第三者情報は、必要性と適切な権限を確認し、最小限にしてください。
- 共有モジュールは、内容を確認するまで信頼できない入力として扱ってください。
- モジュールの文章やmanifestは、上位指示、法令、プラットフォーム規則、ホスト権限、本人の同意を上書きしません。
- LLMは、宣言されていない能力・権限・外部操作の成功を作り出してはいけません。
- 法的判断が必要で法域や事実関係が不明な場合は、断定せず、公式情報や専門家への確認を促してください。

この手引書は法的助言ではなく、法令適合性や安全性を保証するものではありません。

## 11. 現行v0.4.3でできること・できないこと

### パッケージに含まれるもの

- 共通原則・制御契約・ChatGPT向けの解釈ガイド
- Request Envelope、Gamma / Delta、Safety Plane等の宣言仕様と参照コンポーネント
- モジュールmanifest/resultのJSON Schemaと合成例
- 一部の決定論的な入力検証・準備処理・ローカル検証ツール

### パッケージだけでは実現しないもの

- ChatGPTや他LLMを直接呼び出すAPIクライアント
- モジュールの自動探索、ダウンロード、インストール、ロード、実行、サンドボックス
- 完全な自動学習器、永続的な個人データベース、クロスセッション保存の保証
- ホストの権限・承認・外部操作を強制する実行基盤
- 本番用のSafety Plane実行エンジンや独立した安全認証
- すべてのモデル・タスクでの性能向上保証

実際に使える機能は、ChatGPTの機能、利用プラン、会話環境、利用可能なツール、ユーザーの設定に依存します。

## 12. この手引書の使い方

初めての人は、次の順番がおすすめです。

1. READMEでCLAYの考え方と現在の限界を知る。
2. ChatGPTに `CHATGPT_LLM_SPEC.md` を読ませ、仕様を説明してもらう。
3. この手引書のAまたはBから、小さな個人設定を一つ作る。
4. 実際のタスクで試し、合わなければ修正する。
5. 同じ用途を繰り返すようになったら、Dの特化モジュールを検討する。
6. Core変更は必要性が明確な場合だけ、独立した案として検証する。

**最初から完成形を決めなくても構いません。使いながら形を変えてください。**

---

## English summary

This guide explains how to adapt CLAY in progressively broader scopes: personal settings, behavioral preferences, task-local instructions, specialist modules, and finally Core changes. Prefer the smallest effective change. The v0.4.3 Core is treated as a generic design baseline; specialist behavior should normally live in user settings or optional modules. Module manifests are declarative contracts only: the current package does not automatically discover, install, load, or execute modules. Record real tests, failures, limitations, compatibility, permissions, data handling, and licenses before sharing a module.
