# Terminology across languages

## Rules

1. **Never translate literals.** Commands (`/aidlc`, `$aidlc`, `aidlc config`),
   flags, scope names (`express`, `feature`, ...), file paths, IDs (`FR1`),
   setting names (`Guard Policy`), log and event names (`GATE_APPROVED`), and
   labels the tools print (**Approve**, **Request Changes**, **Guide me**,
   **Continue automatically**, Kiro's **Autopilot** / **Supervised**). Write
   them in English and add a short gloss in the user's language. For an event
   name, the gloss says what it records.
2. **Concepts: the natural local word first, English in parentheses**, on
   first use, then the same word every time. A bare transliteration that
   readers can't parse (for example インテント, ハーネス, エフォート in Japanese)
   is worse than a plain local word.
3. **Match what the user will see on screen.** AI-DLC's own screens say
   "plan" when offering a scope ("I'd run the "mvp" plan ... 19 stages, 19
   approval gates"), so call a scope a plan in conversation.
4. **One concept, one word, and different concepts never share a word.**
   *Reviewers* (the two review agents that challenge output at a gate) and
   *support agents* (domain experts who join a stage when collaborators are on)
   are different things. Keep their names apart.
5. For a language not listed below, apply the same rules: plain local
   wording for concepts, English for literals.

## Japanese (based on feedback from Japanese test users)

| English | Use in Japanese | Avoid / notes |
|---|---|---|
| AI-DLC | AI-DLC（初出のみ「AI 駆動開発ライフサイクル」と添える） | Don't repeat the long translation |
| harness | AI コーディングツール（harness） | ハーネス alone isn't understood |
| engine | エンジン（AI ではない通常のプログラム） | 「決定的なプログラム」 reads like a stiff literal translation |
| conductor | 進行役の AI（`/aidlc` セッション） | コンダクター alone |
| intent | 作業単位（intent） | インテント alone isn't understood |
| space | チームの作業領域（space） | |
| phase / stage | フェーズ / 工程（stage） | ステージ is also fine |
| scope / workflow profile | プラン（scope）。種類は `express`、`feature` など | 「スコープ」 reads as "range". Leave "workflow profile" untranslated or omit it |
| composer | 計画の提案役エージェント（composer） | |
| agent | エージェント（担当分野を持つ AI の役） | |
| reviewer | レビュー用エージェント | Not the same as 支援エージェント |
| support agent / collaborators | 支援エージェント（その工程に加わる専門家役） | Not the same as reviewers |
| approval gate | 承認ゲート（承認ポイント） | |
| verification gate | フェーズ間の自動検証 | |
| Request Changes | **Request Changes**（修正依頼） | Keep the label in English |
| accepted (open findings) | リスク受容として記録 | 「受け入れたリスク」 is also understood |
| artifact | 成果物 | |
| record dir | 記録フォルダ（`aidlc/spaces/.../intents/...`） | |
| audit trail | 監査証跡 | |
| depth | 詳細度（depth）。値は `minimal` などのまま | 「深さ」 is unnatural |
| test strategy | テストの量（test strategy） | |
| effort / effort preset | 思考量（effort） / 思考量のプリセット | エフォート is read as 工数 (work-hours) |
| Unit | 構築単位（Unit） | |
| Plan Approval | コード計画の承認 | 「プラン承認」 clashes with plan = scope |
| rules / learning loop | ルール / 修正を次回に活かす仕組み（learning loop） | 「学習ループ」 alone is unclear |
| sensor | 自動チェック（sensor） | センサー alone |
| knowledge | ナレッジ（社内標準などの参考資料） | |
| fence / Guard Policy | 安全柵（fence） / `Guard Policy` | Keep the setting name in English; don't mix in ガードポリシー |
| review freeze | レビュー後の変更禁止 | 「凍結」 is unclear |
| guardrail | 安全策 | |
| ceremony | 任意の手続き（ceremony） | |
| turn (end of turn) | AI の応答が終わる時点 | 「ターン」 |
| agent picker (Kiro) | エージェントの選択欄 | 「エージェントピッカー」 |
| steering (Kiro) | steering（Kiro の機能名） | Keep as on screen |
| refactor | リファクタリング | 「リファクタ」 |
| greenfield / brownfield | 新規開発 / 既存コード | |

Phase names: Initialization（初期設定、自動で 1 秒未満）, Ideation（アイデア創出）,
Inception（要件定義・計画）, Construction（構築）, Operation（運用）. Write
"Inception（要件定義・計画）" on first use. When giving stage counts, say they don't
include the 3 automatic Initialization stages.
