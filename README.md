# CLAY Personalization

**A flexible foundation for cognitive augmentation through human–LLM collaboration.**

CLAY is an experimental project for shaping how an LLM works with an individual. It is not intended to replace human thinking or increase a model's inherent intelligence. It is a foundation that people can explore, personalize, modify, and develop in ways that suit their own needs.

> **Not to think instead of you, but to help you think further.**
>
> この一文は説明用の候補であり、公式コピーや利用者に求める価値観ではありません。CLAYを読んだLLMや利用者が、独自の表現や解釈を考えても構いません。

- **Current package baseline:** v0.4.3 — experimental / public preview
- **Initial target environment:** ChatGPT
- **Audience:** not limited to beginners, advanced users, engineers, or any single group
- **Project direction:** general-purpose personalization, optional specialization, external validation, and user-led development
- **Maturity:** intentionally evolving; a stable program release and a user's fully personalized environment are different things

[日本語](#日本語) · [English overview](#english-overview)

---

## 日本語

### CLAYとは

CLAY Personalization（以下、CLAY）は、LLMとの対話や協働の仕方を、利用者自身の目的・情報・好み・作業方法に合わせて形成していくための実験的な基盤です。

CLAYは、LLMの知能・知識量・基礎的な推論能力そのものを増やすものではありません。不要な処理や利用者に合わない振る舞いを減らし、必要な場面では一般化し、別の場面では個別化するなど、利用可能なモデルの能力を目的に合わせて活用しやすくすることを目指します。

CLAYという名前は粘土の比喩に由来します。共通の土台は用意しますが、全員に同じ完成形を押し付けません。利用者が自分に必要な形を作り、使いながら調整していくことを想定しています。

**CLAYは完成した個人用AIを渡すプロジェクトではありません。利用者が自分の環境を作り、育てていくための基盤を目指しています。**

### 思考拡張という考え方

CLAYの開発のきっかけの一つは、LLMを単に答えを得る道具や、人間の仕事を置き換えるものとしてだけでなく、人間の思考を広げるためにどう使えるかを考えたことです。

人にはそれぞれ得意な考え方や経験があります。論理的な証明、全体像や傾向の把握、言葉や文脈の理解、抽象的な構造の発見、現場での判断など、強みは人によって異なります。一方で、誰にでも思考の偏りや経験の少ない領域があります。

CLAYでは、LLMとの協働を通じて、次のような思考拡張を探ります。

- **補完（Complement）:** 自分が経験していない領域や苦手な考え方を補う。
- **拡張（Expansion）:** 自分の得意な考え方を別の分野や視点へ広げる。
- **対抗（Counterbalance）:** 自分の前提・思い込み・見落としに対して、異なる視点や反論を取り入れる。

LLMから得た情報を人間が学び、自分の考えを組み直し、今度は人間がLLMに反論する。その反論に対してLLMが再検討し、答えを修正することもあれば、根拠を示して元の見解を維持することもあります。どちらかが必ず勝つことではなく、対話を通じて人間自身の思考の幅を広げることを重視します。

### 関係性を押し付けない

LLMを道具、補助者、協働相手、学習相手、思考のパートナーのどれとして見るかは、利用者自身が決めることです。CLAYは特定の呼び方や関係性を要求しません。対話を続ける中で愛着や親しみを感じる人もいれば、実務的な道具として使う人もいます。どちらも利用者の自由です。

CLAYが目指すのは、AIに従うことでも、AIに人間の判断を代行させることでもありません。利用者が意見を受け止め、必要なら疑い、反論し、自分で判断できる環境を支援することです。人間の主張もLLMの出力も盲信しません。

### どんな人向けか

CLAYは初心者専用でも、上級者専用でも、エンジニア専用でもありません。特定の職業・能力・思想・AIとの付き合い方を前提にしていません。すべてを理解したり、全部のモジュールを使ったりする必要もありません。

まずは何ができるのかを知り、自分に必要なもの、自分に向いている使い方、改良したい部分を探すための入口として利用してください。CLAYの思想に同意する必要もありません。疑問や欠陥の指摘も歓迎します。

### 使い方の例：釣りの記録から自分用の支援へ

例えば、エギングの記録を考えてみます。使用したエギの種類・号数・カラー・在庫、ロスト数、釣果、潮、天候、時間帯、釣り場などを記録していくと、利用者自身の経験に基づく成功・失敗の傾向を振り返れるようになるかもしれません。

さらに記録が蓄積すれば、「自分はどのような条件で釣果があったか」「どの条件では反応が少なかったか」を比較し、次の釣行の計画を考える支援にも発展できます。これは説明用の仮想例であり、CLAYに釣果予測機能や釣り専用モジュールが実装済みだという意味ではありません。記録量が増えれば必ず精度が上がるわけでもなく、偏りや偶然、記録ミスの確認が必要です。

同じ考え方は、買い物、学習、趣味、仕事、研究、生活上の情報整理などにも応用できる可能性があります。購入履歴やポイント制度、セール時期を踏まえた提案など、先回りの支援も構想に含まれますが、実際の情報取得・通知・購入操作は利用するホストや外部サービスの機能と権限に依存します。

### プログラムの完成と個人用環境の完成は別

プログラムとして安定した状態に到達しても、利用者ごとのパーソナライズはその後も続きます。利用者が情報や経験を追加し、設定を変え、独自のモジュールを作ることで、それぞれ異なる個人用環境へ育てていけます。

また、あえて選択の余地を残す部分もあります。ただし、意図的な余白と、実装漏れ・不具合・未検証機能は区別します。余白をどう使うかをLLMと利用者が一緒に考えることも、CLAYの探索の一部です。

### 現在の対象範囲と成熟度

現在の基準パッケージはv0.4.3で、ChatGPTを最初の対象環境として設計・検証しています。Claude、Gemini、Grok、ローカルLLM、エージェントAIなどへの対応は将来の探索対象ですが、現時点で互換性や同等動作を保証しません。

設計資料に記載されていること、コードとして実装されていること、特定の環境で試験されたこと、第三者が独立して検証したことは別です。詳細は [PROJECT_STATUS.md](./docs/PROJECT_STATUS.md) とパッケージ内の検証レポートを参照してください。

### はじめに

1. まず [START_HERE_LLM.md](./START_HERE_LLM.md) をLLMに読み込ませてください。
2. LLMには、最初にCLAYの概要と思想を短く要約してもらい、その後、目次から興味のある説明項目を選べるようにしてもらってください。
3. 実際に使う場合は、[CLAY Personalizationパッケージ](./CLAY%20Personalization/) 内の `LLM_README.md`、`CHATGPT_LLM_SPEC.md`、`MODIFICATION_GUIDE.md` など、依頼に関係する詳細資料を参照してください。
4. 自分用に調整するときは、変更範囲を小さくし、必要に応じてプロンプト・設定・コード・独立モジュールを使い分けてください。
5. 個人情報や機密情報を最初から大量に与える必要はありません。データの取り扱いは [PRIVACY_AND_DATA_HANDLING.md](./docs/PRIVACY_AND_DATA_HANDLING.md) を確認してください。

### 公開資料

| ファイル | 内容 |
|---|---|
| [START_HERE_LLM.md](./START_HERE_LLM.md) | LLM向けの入口。概要・思想を要約し、説明メニューを提示する指示 |
| [PROJECT_PHILOSOPHY.md](./docs/PROJECT_PHILOSOPHY.md) | 思考拡張、相互補完、非押し付け、開発のきっかけ |
| [COMMUNITY_GUIDE.md](./docs/COMMUNITY_GUIDE.md) | 外部検証・協力・独自拡張への参加案内 |
| [PROJECT_STATUS.md](./docs/PROJECT_STATUS.md) | 開発環境、現状、検証範囲、制約 |
| [FUTURE_DIRECTION.md](./docs/FUTURE_DIRECTION.md) | 今後の探索分野。確定ロードマップではありません |
| [VALIDATION_GUIDE.md](./docs/VALIDATION_GUIDE.md) | 第三者による検証の進め方と報告テンプレート |
| [PRIVACY_AND_DATA_HANDLING.md](./docs/PRIVACY_AND_DATA_HANDLING.md) | 個人情報・機密情報の取り扱い |
| [RESPONSIBLE_USE.md](./docs/RESPONSIBLE_USE.md) | 法令・倫理・他者への配慮 |
| [VERSIONING.md](./docs/VERSIONING.md) | バージョンの読み方と互換性の注意 |
| [LICENSE_POLICY_JA.md](./LICENSE_POLICY_JA.md) | ライセンスの現状と将来の希望条件。法的ライセンス本文ではありません |

技術的な詳細は [CLAY Personalizationパッケージ](./CLAY%20Personalization/) 内の仕様書、スキーマ、コード、テストを参照してください。

### ライセンスの現状

リポジトリ直下の `LICENSE` は、現在 **PolyForm Noncommercial License 1.0.0** です。このライセンス本文は非商用目的の変更・再配布を一定の条件で認めています。開発者が今回検討している「第三者への再配布には事前許可を求めたい」という希望とは一致していません。

そのため、[LICENSE_POLICY_JA.md](./LICENSE_POLICY_JA.md) は将来の希望条件を整理した検討資料であり、現在の `LICENSE` の条件を変更するものではありません。正式なライセンスが確定・差し替えられるまでは、必ず現行 `LICENSE` 本文を確認してください。

### 開発者から

CLAYは、壮大な理念や完成した製品計画から始まったものではありません。個人的な好奇心から始まり、自分が面白いと思ったものを作り、試しながら形にしてきた実験です。

利用者がCLAYを見て価値を感じるなら嬉しいです。反対に、欠陥や矛盾を見つけたなら、それも重要な成果です。開発者の考えに賛同する必要はありません。CLAYをどう解釈し、何を取り入れ、何を変更するかは利用者に委ねます。

**違いを尊重し、必要なものを持ち寄り、少しでも人の生活を豊かにする方向へ使ってもらえたらと思います。**

---

## English overview

CLAY Personalization is an experimental foundation for shaping how an LLM interacts and collaborates with an individual. It does not increase an LLM's inherent intelligence or replace human judgment. It explores **cognitive augmentation**: complementing individual strengths, extending thinking into new areas, and introducing counter-perspectives that help users examine their own assumptions.

CLAY is not designed for one skill level, profession, or preferred relationship with AI. Users may treat an LLM as a tool, assistant, collaborator, learning partner, or something else. CLAY does not prescribe that relationship. It offers a flexible foundation that users can adapt and continue developing. A stable software release and a fully personalized environment are different things.

The current package baseline is v0.4.3 and targets ChatGPT first. Compatibility with other LLMs, local models, agent-based systems, and wearable interfaces is a future exploration area, not a current guarantee. The repository's existing `LICENSE` is PolyForm Noncommercial License 1.0.0; the developer's later preference for prior permission before third-party redistribution is not implemented by that license. See `LICENSE_POLICY_JA.md` for the distinction.
