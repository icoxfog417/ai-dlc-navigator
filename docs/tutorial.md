# AI-DLC v2 の中核を学ぶ : 判断をルールとして蓄積し、検証に生かす（45 分）

AI-DLC v2 の中心となる考え方を、簡単な割り勘計算を行う CLI アプリケーションの作成を通じて体験します。

> [!NOTE]
> **所要時間**
>
> 約 45 分です（準備の時間は含みません）。手順ごとの目安は「[題材と時間配分](#題材と時間配分)」を参照してください。
> AI-DLC 2.11.4 と Claude Code で動作を確認しています。

> [!NOTE]
> AI の生成結果は一定ではないため、チュートリアル通りに進むとは限らない点に留意ください

## このチュートリアルで体験すること

人間（判断者）が下した**判断**を、次の流れでルールとして蓄積し、検証に生かします。

1. 判断: reviewer の指摘を受けて、判断者が AI エージェントに修正を指示する
2. 学習: 指示した内容が、`memory/project.md` にルールとして保存される
3. 検証: 判断者がルールを要件書のテンプレートとして配置すると、sensor が LLM を使わないプログラムで、要件書がルールに沿っているかを検査する
4. 次の作業: AI エージェントが最初からルールに従って成果物を作成するため、reviewer は内容の確認に集中できる

これらの経過は、すべて `audit/` に記録されます。また途中で、**誤った判断に気づいて前の stage に戻る**操作も体験します。

### 用語

このチュートリアルで使う言葉を、次のように定義します。人間である判断者と、AI-DLC の reviewer は区別して記載します。また `advisory` という語は、AI-DLC の 2 か所で異なる意味に使われます。

| 言葉 | 意味 |
|---|---|
| 判断者 | このチュートリアルを進める人間。reviewer の指摘を受けて AI エージェントに修正を指示し、承認ゲートで承認するかどうかを決める |
| reviewer | AI-DLC の中で成果物を確認し、指摘を返す LLM エージェント（product lead、architecture reviewer など）。人間ではない |
| review の強さ `advisory` / `adversarial` | reviewer の確認を 1 回で終えるか、AI エージェントによる修正と reviewer の再確認を繰り返すか |
| sensor の扱い `advisory` / `blocking` | LLM を使わないプログラムによるチェックの結果を通知するだけか、不合格のときに承認ゲートで先に進めないようにするか |
| intent | AI-DLC で 1 つの依頼に対応する作業の単位。手順 1 で 1 つ目、手順 6 で 2 つ目の intent を開始する |
| memory | 従うべきルールや書式。やり取りから学習されるほか、手動でも編集できる |
| knowledge | 参考資料。ファイルを取り込んで使う（今回は使わない） |

### 題材と時間配分

題材は **割り勘 CLI（TypeScript / Node.js）** です。

| パート | 内容 | 目安 |
|---|---|---|
| 手順 1〜4 | 判断・学習・Requirements Analysis への戻り・audit の確認 | 約 32 分 |
| 手順 5〜6 | ルールのテンプレート化と、2 つ目の intent での確認 | 約 13 分 |
| 合計 | | **45 分** |

---

## 0. AI-DLC の準備（※所要時間外）

**必要なツール**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
- AI-DLC（`aidlc` コマンド）。インストール方法は [AI-DLC の公式ドキュメント](https://github.com/awslabs/aidlc-workflows) を参照してください
- Node.js と git

> [!TIP]
> **ai-dlc-navigator を補助として使う**
>
> [ai-dlc-navigator](index.md) は、AI-DLC を初めて使う人を案内する Agent Skill です。必須ではありませんが、インストールしておくと、セットアップで迷ったときや、チュートリアルの途中で承認ゲートや sensor の意味が分からないときに、Claude Code の会話で質問できます。
>
> ```bash
> gh skill install icoxfog417/ai-dlc-navigator ai-dlc-navigator --agent claude-code --scope user
> ```
>
> 質問の例: `/ai-dlc-navigator aidlc doctor の警告の意味を教えて`
>
> navigator は説明だけを行います。stage を進める操作や承認ゲートでの回答は、判断者が行います。

**練習用のプロジェクトを作成する**

ターミナル（Claude Code の外）で空のフォルダを作成し、AI-DLC をセットアップします。
※ `--harness` の値は、使用する AI Coding Agent によって異なります

```bash
mkdir ~/aidlc-playground && cd ~/aidlc-playground
git init
aidlc config --harness claude          # 質問には推奨デフォルト（選択肢 1）を選ぶ
aidlc doctor
git add -A && git commit -m "tutorial baseline" && git tag tutorial-baseline
```

最後の行では、現在の状態を commit し、その commit に `tutorial-baseline` というタグを付けています。[リセット](#リセットもう一度最初から) の際は、この commit まで戻せます。

> [!TIP]
> **doctor の警告について**
>
> - 「Project runtime stamp」の警告が出た場合は、マシンにインストールされた AI-DLC が更新され、プロジェクト側とバージョンが一致していません。`aidlc config --harness claude` を再実行してバージョンを揃えてから、最後の行（commit とタグ付け）を実行してください
> - 「hooks have not run」と「uncommitted change(s)」の警告は、この時点では正常です

完了したら、**このフォルダで新しい Claude Code の会話を開始してください**。`/aidlc` と hook は、会話の開始時に読み込まれます。

---

## 1. AI-DLC の開始 : scope を指定（約 1 分）

Claude Code で次のように入力します。

```text
/aidlc express --review advisory --learnings on --sensors on --skip deployment-pipeline,deployment-execution,observability-setup 割り勘CLIをTypeScriptで作りたい。合計金額と人数を渡すと1人あたりの金額を出す
```

- `express` は最も簡素な進め方（scope）です。既定では reviewer・sensor・learnings がすべて off のため、`--review`・`--sensors`・`--learnings` の 3 つのフラグで on にします
- `--review advisory` で、reviewer の確認を 1 回にします。所要時間内に収めるため、`adversarial` は使いません
- `--skip` で、デプロイ関連の 3 つの stage（Deployment Pipeline、Deployment Execution、Observability Setup）を plan から外します。指定しない場合、Build and Test の承認ゲートで、これらの stage を外すかどうかを確認されます

<!-- trial -->
確認:
- [x] 4 つのフラグを 1 行で受け付けた（`aidlc-state.md` に Review Override = advisory、Sensors / Learnings = on (set by you)）
- [x] 「デプロイや監視は不要」と伝えると、最初からデプロイ関連の stage が plan から除外されるか（試走 1 回目は伝えなかったため、Build and Test で除外するやり取りに 4〜5 分かかった）
  - 試走 2 回目（2026-11-14）: **除外されなかった**。`aidlc-state.md` の Stages to Execute に 4.1 / 4.3 / 4.4 が残り、Build and Test の承認ゲートで「不要なら外すように言ってほしい」と案内された。「Approve。デプロイ関連の3つのステージは不要なのでプランから外してください」と 1 回で返すと 38 秒で完了（`RECOMPOSED`）
- [x] `--skip deployment-pipeline,deployment-execution,observability-setup` を付けると、作成時に plan から外れる（2026-11-14、`tutorial-baseline` の clone で手順 1 のみ確認。`aidlc-state.md` は Plan = tailored plan、Stages to Execute は 2.3 / 3.5 / 3.6 のみ。「3 stages, 3 approval gates」と表示）。根拠: 同梱ドキュメント `docs/guide/12-cli-commands.md` の「Creating a workflow with its own stage changes」
- [x] `--skip` を付けた場合に、Build and Test の承認で intent が完了するか（試走 3 回目: 承認ゲートの選択肢が「Approve — Complete workflow」になり、デプロイ関連の確認なしで完了。`RECOMPOSED` も記録されない。`/aidlc --status` の表示は Scope ではなく `Plan: tailored plan (this piece of work only)`）
<!-- /trial -->

`express` では、次の stage が順に実行されます。詳細は [Stage-by-Scope Matrix](https://awslabs.github.io/aidlc-workflows/guide/05-scopes-and-depth/#stage-by-scope-matrix) を参照してください。

| # | フェーズ | stage | このチュートリアルでの扱い |
|---|---|---|---|
| 0.1〜0.3 | Initialization | Workspace Scaffold / Workspace Detection / State Initialization | 手順 1 の入力後に自動で実行され、承認ゲートはない |
| 2.1 | Inception | Reverse Engineering（既存コードの解析） | 新しいプロジェクトで既存のコードがないため、スキップされる |
| 2.3 | Inception | Requirements Analysis | 手順 2 と手順 3-1 で実行する |
| 3.5 | Construction | Code Generation | 手順 3-1 で実行する |
| 3.6 | Construction | Build and Test | 手順 3-2 で実行する |
| 4.1 | Operation | Deployment Pipeline | 手順 1 の `--skip` で plan から外す |
| 4.3 | Operation | Deployment Execution | 同上 |
| 4.4 | Operation | Observability Setup | 同上 |

---

## 2. Inception : 要件の判断と学習（約 9 分）

1. Requirements Analysis が始まると、AI エージェントが要件に関する質問を `requirements-analysis-questions.md` に書き出し、「How would you like to answer them?」と回答方法を尋ねます。**Guide me**（チャットで質問に順に回答する）を選びます

    > [!NOTE]
    > 回答方法の質問は、1 つの intent につき 1 回だけ、質問のある最初の stage で表示されます。`express` では Requirements Analysis がその stage です。以降の stage では、同じ回答方法が使われます

2. 質問に回答します。端数の扱いの質問には、選択肢を選ばずに、**あえて次のように回答してください**。金額の合計が合わない仕様を作っておき、手順 3-1 でその仕様の誤りに気づいて修正する流れを体験するためです。選択肢には「不足分は幹事が負担」などの処理を含むものがあるため、選択肢からは選びません。質問されなかった場合も、自分から同じように伝えます。そのほかの質問には選択肢 1 を選びます

    ```text
    1人あたりの金額を1円未満切り捨てて表示するだけ
    ```

3. AI エージェントが要件書を作成すると、sensor、reviewer（product lead）の順に確認が実行されます。reviewer の確認には 3 分ほどかかります
4. reviewer の指摘（ID 付き）を確認します。指摘を受けてどのような修正を指示するかは判断者が決めますが、このチュートリアルでは手順をそろえるため、**数値計算の規則を独立させてまとめる**という判断を下します。AI エージェントに次のように指示します。

    ```text
    数値計算の規則（計算式と端数の丸め方）は、ほかの要件から独立させて、具体的な金額の例とともにまとめてください
    ```

5. **「Keep that for next time?」**（次回以降も適用するか）と質問されたら、**Yes, for this project** を選びます
6. 承認ゲートが表示されたら **Approve** します

学習されたルールは、`memory/project.md` の `## Corrections` に追記されます。次のコマンドで確認します。

```bash
tail -n 3 aidlc/spaces/default/memory/project.md
```

次のような行が追加されているはずです。

```text
- 要件書では、数値計算の規則（計算式と端数の丸め方）をほかの要件から独立させ、具体的な金額の例とともにまとめる。 (learned 2026-11-15) <!-- cid:... -->
```

> [!TIP]
> - reviewer は承認を止めません。指摘が未解決のままでも判断者は承認でき、未解決の指摘は受け入れたリスクとして記録されます。これは `advisory` に限らず、`adversarial` でも同じです（`adversarial` では、承認ゲートの前に修正と再確認が最大 2 回繰り返されます）
> - 判断者の指示が、その場限りで終わらず、次回以降のルールとして保存されます

> [!NOTE]
> **「Keep that for next time?」が表示されなかった場合**
>
> 「承認。次からは数値計算の規則を独立させてまとめて」と伝えてください。確認の質問なしでルールとして保存され、保存先が 1 行で表示されます。

<!-- trial -->
確認:
- [x] 「Keep that for next time?」が表示された（audit では `DECISION_RECORDED`、Question Kind = learnings-note）
- [x] `project.md` に `(learned 2026-11-13)` 付きの行が追加された（`RULE_LEARNED`）
- [x] 承認ゲートより前に指示したため、差し戻し（`GATE_REJECTED`）は発生しなかった。ゲートで Request Changes を選ぶ方法でも同様に学習されるはず（未確認）
  - 試走 2 回目: 承認ゲートが表示された後に指示文を送ったため、`GATE_REJECTED`（Feedback = 指示文）→ `STAGE_REVISING` が記録された。それでも「Keep that for next time?」が表示され、`RULE_LEARNED` も記録された → ゲートでの指示でも学習される
  - 試走 2 回目: 「Keep that for next time?」以降、応答が英語になった（その後のターンでは日本語と英語が混在）
- 試走 3 回目: 端数の質問（Q1）の選択肢 2 が「1円単位で切り捨てて、足りない分を表示する（不足の1円は幹事が負担）」で、選ぶと手順 3-1 で修正する内容がなくなる。Other で「1人あたりの金額を1円未満切り捨てて表示するだけ」と回答 → 本文の手順 2 をこの回答文に固定
- 試走 3 回目: 最初の review で指摘 0 件。指示文はそのまま送り、学習の流れは同じだった（`GATE_REJECTED` → 「Keep that for next time?」→ `RULE_LEARNED`）
- [x] 指示文を「数値計算の規則を独立させてまとめる」に変更した版で、同じように「Keep that for next time?」→ `RULE_LEARNED` になるか（試走 1〜3 回目は「受け入れ条件」の指示文。受け入れ条件はルールがなくても AI エージェントが書くことが多く、学習の効果が見えないため変更）
  - 試走 4 回目（2026-11-15）: 表示され、`RULE_LEARNED`。保存された行は「要件定義では、数値計算の規則（計算式と端数の丸め方）をほかの要件から独立した節にまとめ、具体的な金額の例を付ける」。試走 4 回目も、ルールなしで最初の要件書に Given/When/Then が書かれていた
  - 試走 4 回目: AI エージェントは手順 2 の時点で見出しを `## 数値計算の規則` にした。手順 5 で memory のルールを削除するため、手順 6 で節があればテンプレートによるものと判断できる
- [x] 手順 3-1 の指示文（「合計の一致も書いて」を追加）で「Keep that for next time?」が表示され、ルールが追加されるか（試走 2・3 回目の「幹事が負担」だけの指示文では学習されず、`RULE_LEARNED` は手順 2 の 1 回のみ）
  - 試走 4 回目: **表示されなかった**。Modify の質問（Q5）への回答として扱われたため。`stage-protocol-learnings.md` の When to run では、質問するかは AI エージェントが「次回以降も通用する修正か」で判断し、判断者が「次回以降も」と明示した場合は質問なしで保存する。承認ゲートで「承認。次回以降も、数値計算の規則には支払額の合計が合計金額と一致することを書いて」と伝えると保存された（`RULE_LEARNED` 計 2 回）→ 本文の手順 3-1-4 に反映
- [x] 手順 5 でテンプレートを作成したことは audit に記録されるか（試走 4 回目も記録されなかった。試走 3 回目: どの intent の audit にも記録されなかった。intent の外で行う作業のため。試走 2 回目に 2 つ目の intent の中でテンプレートが修正されたことが audit に記録されたかは、リセットで記録が消えたため未確認）
- [x] 「数値計算の規則」の節を書かせると、AI エージェントや reviewer が手順 2 の時点で合計額のずれ（428 円 × 7 = 2996 円）を指摘しないか。指摘された場合も、手順 2 では修正を指示せずに Approve し、手順 3-1 で修正する
  - 試走 4 回目: 指摘されなかった。要件書には「1人あたり金額 × 人数が合計金額に満たなくても、その差額は扱わない」と明記された
<!-- /trial -->

---

## 3. Construction（約 22 分）

### 3-1. Code Generation : 前の stage に戻る（約 20 分）

1. Requirements Analysis を Approve すると、Construction フェーズの Code Generation に進みます。`express` では Code Generation の plan を承認する手順が省略されており、すぐにコードの生成が始まります
2. ここでは、Code Generation の途中で要件書（`requirements.md`）の「数値計算の規則」を見直し、**「切り捨てでは合計額が一致しない」と気づいたことにします**（3000 円 ÷ 7 人 = 428 円で、428 円 × 7 = 2996 円にとどまります）。**Esc キーで Code Generation を中断し**、Requirements Analysis に戻ります

    ```text
    /aidlc --stage requirements-analysis
    ```

    Code Generation の完了を待たずに戻れば、約 5 分を短縮できます。

3. 既存ファイルの扱い（Keep / Modify / Redo）を確認されたら **Modify** を選びます。何を変更するかを質問されたら、AI エージェントに次のように指示します

    ```text
    端数の扱いを「端数は幹事が負担する」に変更してください。幹事も人数に含め、幹事は1人あたりの金額に端数を上乗せして払います。数値計算の規則には、支払額の合計が合計金額と一致することも書いてください
    ```

4. Requirements Analysis の承認ゲートで、次のように伝えて Approve します。合計の一致を、次回以降も守るルールとして保存するためです（このやり取りでは「Keep that for next time?」は表示されず、そのまま保存されます）

    ```text
    承認。次回以降も、数値計算の規則には支払額の合計が合計金額と一致することを書いて
    ```

5. Code Generation が再実行されます。今回は最後まで進め、architecture reviewer の指摘を確認してから Approve します（Code Generation と review で約 8 分）

> [!TIP]
> 前の stage に戻っても既存のファイルは削除されず、Keep / Modify / Redo から扱いを選べます。完了した stage に戻ってやり直せる点で、ウォーターフォール型の進め方とは異なります

<!-- trial -->
確認:
- [x] 戻った記録は `STAGE_JUMPED`（`Direction: BACKWARD`。やり直しで無効になった後続の成果物も記録される）
- [x] Modify を選んだ記録は `ARTIFACT_REUSED`（Decision: modify）
- 試走 1 回目は、Code Generation の開始から 3 分で戻った
- 試走 2 回目: plan の 1 行（「コード生成の計画から書きます」）は開始から約 30 秒で表示。戻ったのは開始から約 6 分後で、その時点でコードとテスト（31 件）の生成はほぼ終わっていた
- 試走 2 回目: Modify を選ぶと「何を変更するか」（Q5）、端数の変更を指示すると「幹事を人数に含めるか・どう表示するか」（Q6、3 択）を追加で質問された。幹事も人数に含め、幹事が端数を上乗せして払う（`1人あたり: 3,333円` / `幹事: 3,334円`）を選んだ。→ 手順 3 の指示文に、幹事を人数に含めることと上乗せの方法を加えた。試走 3 回目: Q5（何を変更するか）は出たが、この指示文への追加の質問はなく、そのまま要件書が修正された
- [ ] 「気づいたことにして」Esc キーで中断する手順を、Claude Code の画面上の Esc キーで実行できるか（未確認）
- 試走 3 回目: plan の 1 行はメインの会話に表示されなかった（subagent の中で出力された）。`src/` への最初の書き込み（開始から 176 秒）で中断して戻った。中断は Esc キー相当の操作（プロセスへの割り込み）で行い、Esc キーそのものは未確認 → 本文は「要件書を見て気づいたら Esc で中断」に変更
- 試走 3 回目: 戻った後の Requirements Analysis の review で Major の指摘 1 件（FR1.1 の出典が Q5 で置き換えた Q1 のまま）。Approve して進めた
- 試走 2 回目: Code Generation の再実行は最初からではなかった。既存のコードを残し、変更分を Step 9 として plan に追加した（再実行と review で約 7 分）
<!-- /trial -->

### 3-2. Build and Test : intent の完了（約 2 分）

Build and Test では、テストが実行されます。結果を確認して Approve すると、この intent は完了です。

---

## 4. 完了後 : audit で履歴を確認する（約 3 分）

ここまでのやり取りがどのように記録されたかを確認します。まず Claude Code で次のように入力します。

```text
/aidlc --status
/aidlc-replay
```

続けてターミナルで、audit のファイルを直接確認します。

```bash
# どのイベントが何回記録されたか
grep -h '^\*\*Event\*\*' aidlc/spaces/default/intents/*/audit/*.md | sort | uniq -c | sort -rn
# ルールの学習・Requirements Analysis への戻り・Modify の記録
grep -n -A8 'RULE_LEARNED\|STAGE_JUMPED\|ARTIFACT_REUSED' aidlc/spaces/default/intents/*/audit/*.md
# sensor がどの stage で何回合格したか
grep -h -A6 'SENSOR_PASSED' aidlc/spaces/default/intents/*/audit/*.md | grep -E 'Sensor ID|Stage slug' | paste - - | sort | uniq -c
```

注目するイベント:

| イベント | 意味 |
|---|---|
| `DECISION_RECORDED` / `QUESTION_ANSWERED` | AI エージェントが判断者に尋ねた質問と、その回答（「Keep that for next time?」を含む） |
| `RULE_LEARNED` | ルールが学習された記録（保存先と見出し付き） |
| `REVIEW_REQUESTED` / `REVIEW_COMPLETED` | reviewer に確認を依頼した / 確認が完了した記録 |
| `STAGE_JUMPED` | 前の stage に戻った記録 |
| `ARTIFACT_REUSED` | 戻った先の stage で、既存ファイルを Keep / Modify した記録 |
| `SENSOR_FIRED` / `SENSOR_PASSED` / `SENSOR_FAILED` | sensor の実行 / 合格 / 不合格 |
| `GATE_APPROVED` / `GATE_REJECTED` | 承認 / 差し戻し |
| `RECOMPOSED` | plan から stage を除外した / 追加した記録 |
| `CHANGE_ACCEPTED` | review 後のファイル変更を検知したうえで、そのまま進めた記録 |

> [!NOTE]
> **合格した sensor の結果は表示されません**
>
> sensor の結果が承認ゲートで報告されるのは、指摘が残っている場合だけです。sensor が実行されたことは audit で確認します（`required-sections` / `upstream-coverage` / `traceability` が数十回実行されているはずです）。

> [!NOTE]
> **設定変更の記録について**
>
> 手順 1 のように開始時にフラグで設定した場合、設定変更のイベント（`CEREMONY_SET` / `REVIEW_CLASS_CHANGED`）は記録されません。設定は `aidlc-state.md` に `set by you` として記録されます。

<!-- trial -->
試走 1 回目: sensor は 26 回実行され、26 回とも合格。`CHANGE_ACCEPTED` の対象は `.gitignore`（Code Generation で `node_modules/` と `dist/` が追記された）。

試走 2 回目: sensor は 44 回実行され、44 回とも合格（`required-sections` 34 回、`upstream-coverage` 8 回、`traceability` 2 回）。`CHANGE_ACCEPTED` は記録されなかった（AI エージェントは `.gitignore` を変更せず、追記を判断者に提案しただけ）。`GATE_REJECTED` 1 回、`RECOMPOSED` 1 回（デプロイ関連の stage の除外）。`/aidlc-replay` の Duration は 32 分。
<!-- /trial -->

---

## 5. 2 つ目の intent の準備 : ルールをテンプレートにする（約 1 分）

手順 2・手順 3-1 で学習された数値計算の規則のルールを、要件書のテンプレートとして `memory/templates/` に配置します。これにより、AI-DLC に同梱されている `required-sections` という sensor が、要件書に必要な見出しがそろっているかを、LLM を使わないプログラムで検査するようになります。sensor を自作する必要はありません。

ルールを sensor の検査対象にするかどうかも、判断者が決めます。Claude Code で次のように依頼します。

```text
memory/project.md の数値計算の規則に関するルールを、要件書のテンプレートとして aidlc/spaces/default/memory/templates/ に置いてください。数値計算の規則は「## 数値計算の規則」の節にし、ほかの見出しは今回の要件書に合わせてください。説明は HTML コメントに書き、コメントの中では行頭に ## を書かないでください。テンプレートに移したルールは project.md から削除してください
```

- `aidlc/spaces/default/memory/templates/requirements.md` が作成されます。ファイル名は成果物の `requirements.md` と同じです
- 手順 2 のルールは、数値計算の規則をまとめることだけを求めていて、見出しの名前は決めていません。テンプレートで `## 数値計算の規則` という節にすると、その節があるかを `required-sections` が検査するようになります

テンプレートと project.md の内容を確認してから、commit しておきます。

```bash
git add aidlc/spaces/default/memory && git commit -m "Add requirements template"
```

> [!NOTE]
> **AI エージェントはテンプレートも修正できます**
>
> AI-DLC は、AI エージェントが memory のテンプレートを修正することを禁止していません。sensor が不合格になったときに、要件書ではなくテンプレートが修正される場合もあります。テンプレートを commit しておけば、`git diff aidlc/spaces/default/memory/` で変更を点検できます。

---

## 6. Inception（2 つ目の intent） : テンプレートの効果を確認（約 12 分）

Claude Code で、2 つ目の intent を開始します。

```text
/aidlc express --review advisory --learnings on --sensors on --skip deployment-pipeline,deployment-execution,observability-setup 割り勘CLIに、人ごとに重みを付ける傾斜配分を追加したい
```

2 つ目の intent では既存のコードがあるため、最初に Reverse Engineering が実行されます（約 5 分）。完了したら Approve します。続く Requirements Analysis では、回答方法に **Guide me** を選び、重みの指定方法の質問には、選択肢を選ばずに「`warikan 10000 --weights 2,1,1` のようにオプションで渡し、重みの個数を人数とする」と回答し、そのほかの質問では選択肢 1 を選びます。

Requirements Analysis の承認ゲートまで進め、次の 3 点を確認します。

1. AI エージェントに指示しなくても、要件書に `## 数値計算の規則` の節があり、傾斜配分の計算式と端数の丸め方が書かれている → **テンプレートが適用された**
2. `required-sections` が `SENSOR_PASSED` になっている → **sensor が検査した**
3. reviewer の指摘が書式ではなく、内容（重みの扱いなど）に集中している → **形式は sensor が、内容は reviewer が確認し、判断者が承認するかどうかを決める**

確認が終わったら、`/aidlc park`（中断）で終了して構いません。

<!-- trial -->
確認（**最重要**。試走 2 回目（2026-11-14）で確認）:
- [x] `required-sections` がテンプレート `requirements.md` を参照したか（合格の audit 行だけでは判別できない場合は、AI-DLC 側で「requirements.md に対して required-sections はどのテンプレートを使った？」と質問する）
  - 参照した。手順 5 で AI エージェントが作成したテンプレートの HTML コメント内に「## 見出しはこの順・この表記のまま残すこと」という行があり、これが必須の見出しとして数えられて `SENSOR_FAILED`（required-sections、Findings count 1）。AI エージェントがテンプレートのその行を修正し、`SENSOR_PASSED` になった
  - AI エージェントが memory のテンプレートを修正することは、AI-DLC では禁止されていない（`stage-protocol.md` の Template overrides はテンプレートを「hand-authored override」とするだけで、修正を止める hook もない）。対策として、手順 5 の指示文に「コメントの中では行頭に ## を書かない」を加えた
- [x] 手順 5 の指示文の変更（`## 数値計算の規則` の追加、コメント内の `##` の禁止）を反映した状態で、2 つ目の intent の要件書に `## 数値計算の規則` が含まれるか
  - 試走 3 回目: 含まれた。傾斜配分の計算式（幹事以外は floor(T × wᵢ ÷ W)、幹事は残り）、丸め、端数の負担、合計の一致と例、値の範囲、境界値が書かれた。テンプレートのコメント内に `##` の行はなく、sensor は 12 回とも合格（`SENSOR_FAILED` なし）。`git diff aidlc/spaces/default/memory/` は空で、テンプレートは修正されなかった
- [x] 2 つ目の intent では既存のコードがあるため、Reverse Engineering が実行されるか（実行されると所要時間が延びる）
  - 実行された（約 5 分、承認ゲートあり）。2 つ目の intent の plan は 7 stage・承認ゲート 7 つ
- [x] AI エージェントが要件書を作成する際に、テンプレートを雛形として使ったか
  - 使った。指示なしで `## 受け入れ条件` を含む 10 個の見出しがテンプレートの順にそろっていた
- [x] reviewer の指摘が内容に集中するか: 試走 2 回目は指摘 0 件（No blocking concerns）のため確認できなかった
  - 試走 3 回目: 指摘 2 件（Minor）。R-01 は重みの合計がオーバーフローする境界の受け入れ条件がないこと、R-02 は出力の文言が未確定なこと。どちらも内容に関する指摘で、書式の指摘はなかった
- [x] 2 つ目の intent でも `--skip` でデプロイ関連の stage が外れるか（試走 3 回目: 外れた。Stages to Execute は 2.1 / 2.3 / 3.5 / 3.6）
- 試走 4 回目（手順 5 で memory のルールを削除した版）: 要件書に `## 数値計算の規則` があり、テンプレートのコメントどおり「計算式」「規則」「具体例」の小見出し、合計の一致の規則（FR2.3）、検算の列付きの金額例の表が書かれた。sensor は 12 回とも合格、`git diff aidlc/spaces/default/memory/` は空。reviewer の指摘は Major 1 件（金額 × 重みが安全な整数を超える場合の計算精度。内容に関する指摘）
- 試走 4 回目: 重みの指定方法の選択肢に `--weights` がなかった（人数の代わりに重みを並べる / 名前と重みの組 / 重みごとの人数）。Other で「`--weights 2,1,1` のようにオプションで渡す」と回答すると、人数の引数の扱いを追加で質問された（Q6）→ 本文の回答を「`warikan 10000 --weights 2,1,1` のようにオプションで渡し、重みの個数を人数とする」に固定
- 試走 3 回目の質問は 4 件（重みの指定方法 / 重みの値 / 端数の扱い / 均等割りを残すか）。重みの指定方法の選択肢 1 は「人数の代わりに重みを並べる」で、均等割りを残す場合と区別できないため、選択肢 2（`--weights`）を選んだ。本文の指示を「`--weights` で渡す選択肢」に変更
- 試走 2 回目の質問は 4 件（既存の均等割りを残すか / 重みの種類 / 端数の扱い / 重みの指定方法）。すべて選択肢 1 を選んだ

アイデア: テンプレートにあえて見出しを 1 つ追加しておくと、`SENSOR_FAILED` → AI エージェントが自ら修正 → `SENSOR_PASSED` の流れが audit に記録され、sensor の効果を示せる。（試走 2 回目では、上記のとおり意図せずこの流れが起きた。→ 手順 5 で `## 数値計算の規則` を追加する形で本文に反映。ただし AI エージェントはテンプレートを雛形として要件書を作成するため、`SENSOR_FAILED` は起きない可能性が高い）
<!-- /trial -->

---

## 7. 発展編（チュートリアルの外）

- **誤って学習されたルールを削除する**: `project.md` から該当する行を手動で削除します。ルールは削除されますが、`RULE_LEARNED` の記録は audit に残ります
- **承認ゲートで先に進めないようにする sensor**: 「金額に浮動小数を使わない」というチェックを sensor として自作し（`default_severity: blocking` と `fire_on: gate`）、不合格時に Fix findings / Override blocking sensors を選ぶ操作を体験します。learning loop が生成する雛形には `fire_on` が含まれず、チェック本体も自分で実装する必要がある点に注意してください

---

## リセット（もう一度最初から）

Claude Code を終了してから、ターミナルで次のコマンドを実行します。

```bash
cd ~/aidlc-playground
git reset --hard tutorial-baseline
git clean -ndx           # 削除される対象を事前に確認する（この時点では削除しない）
git clean -fdx
aidlc doctor
```

- `-x` が必要です。AI-DLC の実行時ファイル（`aidlc/.aidlc-sessions/`、`intents/.aidlc-engine/`、`runtime-graph.json` など）と `node_modules/`・`dist/` は git の管理対象外のため、`git clean -fd` では削除されません
- `-x` を付けると、使用中の space の記録（`aidlc/active-space`）も削除されます。最後の `aidlc doctor` で、問題がないことを確認してください
- intent だけをやり直す場合は、`/aidlc intent archive <name>` を使う方法もあります。ただし、memory（学習されたルールやテンプレート）は intent の外に保存されているため、削除されません
- 完了したら、新しい Claude Code の会話を開始してください

<!-- trial -->
確認:
- [x] `git clean -fdx` の後、doctor と `/aidlc` が正常に動作するか（試走 3 回目の前に実施: doctor は 0 problems・2 warnings（手順 0 と同じ）、`/aidlc` も正常に開始した）（`active-space` は `tutorial-baseline` の commit の時点から存在したが、gitignore の対象のため削除される。`default` に戻るだけのはず）
<!-- /trial -->

<!-- trial -->
---

## 試走メモ（所要時間）

| 手順 | 目安 | 試走 1 回目 | 試走 2 回目 | 試走 3 回目 | 試走 4 回目 | メモ |
|---|---|---|---|---|---|---|
| 1. 開始 | 1 分 | 0 分 | 1.3 分 | 1.2 分 | 1.4 分 | |
| 2. Requirements Analysis | 9 分 | 9 分 | 7.7 分 | 8.1 分 | 8.4 分 | 3 回目: 回答 → 要件書 + review 4.3 分、書式の指示 → 修正 + 再 review 2.9 分、Keep 0.5 分 |
| 3-1. Code Generation + 前の stage に戻る | 20 分 | 21 分（3 分で戻る + Requirements Analysis やり直し 6 分 + Code Generation の再実行 11 分） | 19.4 分（6.4 分で戻る + Requirements Analysis やり直し 6.1 分 + Code Generation の再実行 6.9 分） | 18.5 分（2.9 分で戻る + Requirements Analysis やり直し 7.1 分 + Code Generation の再実行 8.4 分） | 19.9 分（3.7 分で戻る + Requirements Analysis やり直し 5.6 分 + Code Generation の再実行 10.7 分） | 3 回目: Q6 は出ず、指示文 1 回で Requirements Analysis が完了（6 分） |
| 3-2. Build and Test | 2 分 | 6 分 | 2.8 分 | 2.4 分 | 2.3 分 | 2 回目: デプロイ関連の stage の除外を指示（38 秒）。3 回目: `--skip` のため確認なしで完了 |
| 4. audit | 3 分 | - | 1.1 分 | 1.2 分 | 1.0 分 | `/aidlc --status` と `/aidlc-replay` の処理時間のみ（読む時間を含まない） |
| 小計（1〜4） | 32 分 | 36 分（1〜3 のみ） | 32.2 分 | 31.3 分 | 33.0 分 | |
| 5〜6. テンプレート化 + 2 つ目の intent | 13 分 | - | 13.8 分 | 12.9 分 | 16.0 分（手順 5: 0.9 分、手順 6: 15.2 分） | 3 回目: テンプレート化 0.7 分、Reverse Engineering 5.3 分 + Approve 0.9 分、Requirements Analysis 5.7 分（承認ゲートまで）、park 0.3 分 |
| 合計（1〜6） | 45 分 | - | 46 分（実時間 48 分） | 44.2 分 | 49.0 分 | |

試走 2 回目・3 回目の計測条件: 別プロセスの Claude Code（`claude -p --resume`）に、判断者の入力としてチュートリアルの指示文をそのまま送って計測した。値は AI の処理時間で、判断者が出力を読む・考える時間は含まない（ターン間は約 5 秒）。人間が進める場合は、合計が 45 分を超える見込み。3 回目は 2026-11-15、`--skip`・数値計算の規則のテンプレート・手順 3-1 の新しい指示文を反映した版で実施。4 回目は同日、手順 2 のルールを数値計算の規則に変更し、手順 5 でルールを memory から削除する版で実施。4 回目は Code Generation の再実行（10.7 分）と手順 6 の要件書の作成・review（7.9 分）が長く、45 分を超えた。
<!-- /trial -->
