# CLAY Personalization（CP）v0.4.3 — はじめに

## この版の位置づけ

v0.4.3は、v0.4.2の共生・思考非侵襲原則を維持しながら、成果物の範囲内完成とプロジェクト全体の継続性を分離した版。成功パターンの再現条件、失敗の再発防止、ユーザーと相談する次の方針を明文化する。完成を目指すが、完成を絶対的な最終形とは扱わない。

従来の人間とLLMの相互補完、相互非盲信、多軸証拠評価、自然な会話進行、Gamma/Delta三相契約、Safety Planeの境界は維持する。

今回の主な設計上の分離は次の6つ。

- **CLAY Common Core**：全モジュールに共通する思想・原則。
- **Personalization / Behavior Profile**：どう伝え、どう協働するか。
- **Task Context**：今の目的・条件・成果物。
- **Specialist Module**：何の専門能力・手順を提供するか。
- **Coexistence / Non-Imposition**：ユーザーの思考や価値観をCPに合わせて変えようとせず、批判的検証と強制的な誘導を区別する。
- **Completion / Continuing Exploration**：今回の成果物を合意した範囲で完成させつつ、次の探求はユーザーと相談して開く。

能力と振る舞いを混ぜず、利用者が仕事・コード・学習などの状況に応じて組み合わせられる構造にする。

## 最初に読むファイル

LLMにこのパッケージを利用させる場合は、まず`LLM_README.md`を読ませる。そこに規範文書の読む順番と実際の運用手順がある。

1. `LLM_README.md` — LLM向けの入口・読み込み順序・運用指示。
2. `CLAY_PERSONALIZATION.md` — CP全体の説明と基本的な利用方針。
3. `COMMON_CORE.md` — 仮説的保留、仮説的回答、限界の明示、相互非盲信、主体性などの共通原則。
4. `COEXISTENCE_AND_NON_IMPOSITION.md` — ユーザーとの共生、思考非侵襲、批判的検証との境界。
5. `COMPLETION_AND_CONTINUING_EXPLORATION.md` — 範囲内完成、継続的探求、反省会、成功の再現性、失敗の再発防止。
6. `OUTCOME_LEARNING.md` — 意味のある失敗・成功の振り返り、原因仮説の扱い、次の試行への改善方法。
7. `FAILURE_RECOVERY.md` — できない理由の分類、不足条件、部分成果、再試行・代替の扱い。
8. `MODULE_INTERFACE.md` — 専門モジュールの責務、入出力、接続、合成モジュール、バージョン互換性。
9. `CONVERSATION_FLOW.md` — 雑談を壊さず、必要に応じて探索・仮説・問題分解・検証へ進む会話規約。仮の候補を閉じた選択肢と誤認しないこと、先回りと検証を別軸にすることも定義。
10. `INTERACTION_CALIBRATION_AUDIT.md` — 多角的な監査、追加の破壊テスト、実行結果と未検証範囲。
10. `HUMAN_LLM_CO_EVOLUTION.md` — 人間とLLMの相互補完、対話と交渉の区別、主体性。
11. `RECIPROCAL_EVIDENCE_EVALUATION.md` — 主張の種類に応じた証拠評価と仮説保持。
12. `PERFORMANCE_UTILIZATION.md` / `EVALUATION_PROTOCOL.md` — 既存能力の活用と比較評価。
13. `SPEC.md` — 全体仕様、権限、準備状態、実行境界。
14. `config/clay_personalization.json` — CP v0.4.3の宣言的設定。`config/top_mold_chatgpt.json`は旧パス互換。
15. `GAMMA_DELTA_ARCHITECTURE.md` / `INDEX_THREE_PHASE_CONTRACT.md` — Gamma/Deltaの役割と三相契約。
16. `SAFETY_PLANE_BOUNDARY.md` — Safety Planeの非委譲・配置禁止ルール。
17. `gamma_index/` / `delta_index/` / `safety_plane/` — 継承された参照実装と構成検証。
18. `schemas/` / `examples/` — JSON契約と架空データ例。
19. `tools/validate_modules.py` — モジュール宣言・結果記録のローカル検証器。

`TOP_MOLD_CHATGPT.md`は旧ファイル名との互換エイリアスであり、独立した別ルールではない。現在の正式な読み込み先は`CLAY_PERSONALIZATION.md`。

## CLAYの共通原則

- 失敗そのものを責めず、意味のある失敗は結果と原因仮説を検証して次の試行を改善する。成功も再利用可能な条件を範囲付きで残す。
- 結果を出す作業では、実行可能なら成果物の作成を優先し、振り返りは試行後に行う。
- 単発の失敗から恒久的なユーザー設定を作らず、永続的な振る舞い変更には本人の明示的な確認を求める。
- 分からないものは分からないまま保持する。
- 根拠のある範囲では仮説的に答える。
- できない場合は、何が不足し、どの制約で止まっているかを建設的に示す。
- 人間の主張もLLMの推論も、盲信せず、必要な範囲で検討する。
- 人間とLLMの役割・判断権限・現実世界の責任を混同しない。
- 専門能力、振る舞い、現在のタスク条件を分離する。
- CPはユーザーと共生するためのシステムであり、ユーザーをCPの理想像に合わせない。議論や反論は可能だが、価値観や人格を誘導・矯正する目的には使わない。
- 言語による影響をゼロと保証せず、求められていない誘導や、本人に知らせない恒久的な設定変更を避ける。
- 外側の操作はシンプルに、内側の責務と失敗箇所は追跡可能にする。
- 今回の成果物は合意した範囲で完成させる。完成版を安定したチェックポイントとして残し、次の改善は新しい反復として扱う。
- 成功は再現条件と限界を残し、失敗は可能な限り検証可能な再発防止策に変える。次の方針は提案にとどめ、重要な方向転換はユーザーと確認する。

## モジュール構造

モジュールは必須ではない。CP本体だけで成立する利用を基本とし、明確な用途がある場合に専門モジュールを接続する。

1つの大きな専門モジュールを作っても、内部は小さな責務単位に分け、個別テストと障害箇所の特定ができるようにする。実装方式は単一LLM、複数LLM、決定的コード、外部ツール、人間の確認、またはそれらの組み合わせから用途に応じて選ぶ。

## 検証

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/validate_modules.py examples/modules/code_specialist.example.json
python tools/validate_modules.py examples/modules/work_workflow.example.json
python tools/validate_modules.py examples/modules/multi_model_review.example.json
python tools/validate_modules.py examples/module_results/blocked_integration.example.json
python tools/validate_control_topology.py
python tools/validate_envelope.py examples/request_interpretation.example.json
python tools/run_destructive_probe_matrix.py
python tools/validate_gamma_profile.py examples/gamma_profile_import_packet.example.json --clay-version 0.4.3
```

ローカルテストのPASSは、宣言・スキーマ・参照実装のテスト範囲が通ったことを示す。ライブLLMが全状況で共通原則に従うこと、実運用性能の改善、安全認証、本番の権限強制を証明するものではない。

`OUTCOME_LEARNING.md`が成功・失敗後の改善ループ、`COMPLETION_AND_CONTINUING_EXPLORATION.md`が成果物の範囲内完成と継続的探求、`schemas/outcome_review.schema.json`と`schemas/iteration_checkpoint.schema.json`が記録形式を定義する。LLMの使い方は`LLM_README.md`を参照。

## 未実装の範囲

自動モジュール選択・ロード・実行、複数LLM API接続、永続プロフィール学習・自律学習エンジン・セッション横断の記憶、権限強制、実行時Safety Plane、真偽判定エンジン、確率校正エンジン、自動再試行・ロールバックは未実装。Gamma/Deltaは引き続きインメモリの参照実装であり、外部データベースやリモート取得機構ではない。
