# AI-DLC v2 の中核を学ぶ : 判断をルールとして蓄積し、検証に生かす（45 分）

AI-DLC v2 の中心となる考え方を、簡単な割り勘計算を行う CLI アプリケーションの作成を通じて体験します。

> [!NOTE]
> **所要時間**
>
> 約 45 分です（準備の時間は含みません）。手順ごとの目安は「[題材と時間配分](#題材と時間配分)」を参照してください。
> AI-DLC 2.11.4 と Claude Code で動作を確認しています。

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
| intent | AI-DLC で 1 つの依頼に対応する作業の単位。手順 1 で 1 つ目、手順 5 で 2 つ目の intent を開始する |
| memory | 従うべきルールや書式。やり取りから学習されるほか、手動でも編集できる |
| knowledge | 参考資料。ファイルを取り込んで使う（今回は使わない） |

### 題材と時間配分

題材は **割り勘 CLI（TypeScript / Node.js）** です。

| パート | 内容 | 目安 |
|---|---|---|
| 手順 1〜4 | 判断・学習・Requirements Analysis への戻り・audit の確認 | 約 35 分 |
| 手順 5 | ルールのテンプレート化と、2 つ目の intent での確認 | 約 10 分 |
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
/aidlc express --review advisory --learnings on --sensors on 割り勘CLIをTypeScriptで作りたい。合計金額と人数を渡すと1人あたりの金額を出す。デプロイや監視は不要
```

- `express` は最も簡素な進め方（scope）です。既定では reviewer・sensor・learnings がすべて off のため、`--review`・`--sensors`・`--learnings` の 3 つのフラグで on にします
- `--review advisory` で、reviewer の確認を 1 回にします。所要時間内に収めるため、`adversarial` は使いません
- 最初に「デプロイや監視は不要」と伝えておきます。伝えない場合、Build and Test の途中でデプロイ関連の stage を外すかどうかを確認され、そのやり取りに数分かかります

<!-- trial -->
確認:
- [x] 4 つのフラグを 1 行で受け付けた（`aidlc-state.md` に Review Override = advisory、Sensors / Learnings = on (set by you)）
- [ ] 「デプロイや監視は不要」と伝えると、最初からデプロイ関連の stage が plan から除外されるか（試走 1 回目は伝えなかったため、Build and Test で除外するやり取りに 4〜5 分かかった）
<!-- /trial -->

`express` では、次の stage が順に実行されます。詳細は [Stage-by-Scope Matrix](https://awslabs.github.io/aidlc-workflows/guide/05-scopes-and-depth/#stage-by-scope-matrix) を参照してください。

| # | フェーズ | stage | このチュートリアルでの扱い |
|---|---|---|---|
| 0.1〜0.3 | Initialization | Workspace Scaffold / Workspace Detection / State Initialization | 手順 1 の入力後に自動で実行され、承認ゲートはない |
| 2.1 | Inception | Reverse Engineering（既存コードの解析） | 新しいプロジェクトで既存のコードがないため、スキップされる |
| 2.3 | Inception | Requirements Analysis | 手順 2 と手順 3-1 で実行する |
| 3.5 | Construction | Code Generation | 手順 3-1 で実行する |
| 3.6 | Construction | Build and Test | 手順 3-2 で実行する |
| 4.1 | Operation | Deployment Pipeline | 条件付きの stage。デプロイや監視の作業がない場合はスキップされる |
| 4.3 | Operation | Deployment Execution | 同上 |
| 4.4 | Operation | Observability Setup | 同上 |

---

## 2. Inception : 要件の判断と学習（約 9 分）

1. Requirements Analysis が始まると、AI エージェントが要件に関する質問を `requirements-analysis-questions.md` に書き出し、「How would you like to answer them?」と回答方法を尋ねます。**Guide me**（チャットで質問に順に回答する）を選びます

    > [!NOTE]
    > 回答方法の質問は、1 つの intent につき 1 回だけ、質問のある最初の stage で表示されます。`express` では Requirements Analysis がその stage です。以降の stage では、同じ回答方法が使われます

2. 質問に回答します。**端数の扱いを質問されたら、あえて「切り捨て」を選んでください**（手順 3-1 で、この選択の誤りに気づいて修正します）。質問されなかった場合は、自分から「端数は切り捨てで」と伝えます
3. AI エージェントが要件書を作成すると、sensor、reviewer（product lead）の順に確認が実行されます。reviewer の確認には 3 分ほどかかります
4. reviewer の指摘（ID 付き）を確認します。指摘を受けてどのような修正を指示するかは判断者が決めますが、このチュートリアルでは手順をそろえるため、**要件書の書式を指定する**という判断を下します。AI エージェントに次のように指示します。

    ```text
    要件書には必ず「## 受け入れ条件」の節を設けて、各 FR の受け入れ条件を Given/When/Then で書いてください
    ```

5. **「Keep that for next time?」**（次回以降も適用するか）と質問されたら、**Yes, for this project** を選びます
6. 承認ゲートが表示されたら **Approve** します

学習されたルールは、`memory/project.md` の `## Corrections` に追記されます。次のコマンドで確認します。

```bash
tail -n 3 aidlc/spaces/default/memory/project.md
```

次のような行が追加されているはずです。

```text
- 要件書（requirements.md）には必ず「## 受け入れ条件」の節を設け、各 FR の受け入れ条件を Given/When/Then で書く。 (learned 2026-11-13) <!-- cid:... -->
```

> [!TIP]
> - reviewer は承認を止めません。指摘が未解決のままでも判断者は承認でき、未解決の指摘は受け入れたリスクとして記録されます。これは `advisory` に限らず、`adversarial` でも同じです（`adversarial` では、承認ゲートの前に修正と再確認が最大 2 回繰り返されます）
> - 判断者の指示が、その場限りで終わらず、次回以降のルールとして保存されます

> [!NOTE]
> **「Keep that for next time?」が表示されなかった場合**
>
> 「承認。次からは要件書に受け入れ条件の節を必ず入れて」と伝えてください。確認の質問なしでルールとして保存され、保存先が 1 行で表示されます。

<!-- trial -->
確認:
- [x] 「Keep that for next time?」が表示された（audit では `DECISION_RECORDED`、Question Kind = learnings-note）
- [x] `project.md` に `(learned 2026-11-13)` 付きの行が追加された（`RULE_LEARNED`）
- [x] 承認ゲートより前に指示したため、差し戻し（`GATE_REJECTED`）は発生しなかった。ゲートで Request Changes を選ぶ方法でも同様に学習されるはず（未確認）
<!-- /trial -->

---

## 3. Construction（約 22 分）

### 3-1. Code Generation : 前の stage に戻る（約 20 分）

1. Requirements Analysis を Approve すると、Construction フェーズの Code Generation に進みます。`express` では Code Generation の plan を承認する手順が省略されており、plan が 1 行表示されると、すぐにコードの生成が始まります
2. **その 1 行または要件書（`requirements.md`）を見て「切り捨てでは合計額が一致しない」と気づいたら、すぐに Requirements Analysis に戻ります**（3000 円 ÷ 7 人 = 428 円で、428 円 × 7 = 2996 円にとどまります）

    ```text
    /aidlc --stage requirements-analysis
    ```

    Code Generation の完了を待たずに戻れば、約 7 分を短縮できます。

3. 既存ファイルの扱い（Keep / Modify / Redo）を確認されたら **Modify** を選び、端数の扱いを「端数は幹事が負担する」に変更するよう AI エージェントに指示します
4. Requirements Analysis を再度 Approve すると、Code Generation が最初から再実行されます。今回は最後まで進め、architecture reviewer の指摘を確認してから Approve します（Code Generation と review で約 11 分）

> [!TIP]
> - 前の stage に戻っても既存のファイルは削除されず、Keep / Modify / Redo から扱いを選べます。完了した stage に戻ってやり直せる点で、ウォーターフォール型の進め方とは異なります
> - 手順 2 で学習されたルールは、やり直した Requirements Analysis にも最初から適用されています

<!-- trial -->
確認:
- [x] 戻った記録は `STAGE_JUMPED`（`Direction: BACKWARD`。やり直しで無効になった後続の成果物も記録される）
- [x] Modify を選んだ記録は `ARTIFACT_REUSED`（Decision: modify）
- 試走 1 回目は、Code Generation の開始から 3 分で戻った
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
<!-- /trial -->

---

## 5. Inception（2 つ目の intent） : ルールのテンプレート化と効果の確認（約 10 分）

> [!WARNING]
> **この手順はまだ検証中です**
>
> 手順 5-2 は、実際に動かして確認できていません。結果が説明と異なる場合は、[Issue](https://github.com/icoxfog417/ai-dlc-navigator/issues) でお知らせください。

### 5-1. ルールをテンプレートにする

手順 2 で学習されたルール（受け入れ条件の節）を、要件書のテンプレートとして `memory/templates/` に配置します。これにより、AI-DLC に同梱されている `required-sections` という sensor が、要件書に必要な見出しがそろっているかを、LLM を使わないプログラムで検査するようになります。sensor を自作する必要はありません。

ルールを sensor の検査対象にするかどうかも、判断者が決めます。Claude Code で次のように依頼します。

```text
memory/project.md の「受け入れ条件」のルールを、要件書のテンプレートとして aidlc/spaces/default/memory/templates/ に置いてください。見出しは今回の要件書に合わせてください
```

`aidlc/spaces/default/memory/templates/requirements.md` が作成されます。ファイル名は成果物の `requirements.md` と同じです。

### 5-2. 2 つ目の intent で効果を確認する

Claude Code で、2 つ目の intent を開始します。

```text
/aidlc express --review advisory --learnings on --sensors on 割り勘CLIに、人ごとに重みを付ける傾斜配分を追加したい。デプロイや監視は不要
```

Requirements Analysis の承認ゲートまで進め、次の 3 点を確認します。

1. AI エージェントに指示しなくても、要件書に `## 受け入れ条件` が含まれている → **memory のルールが適用された**
2. `required-sections` が `SENSOR_PASSED` になっている → **sensor が検査した**
3. reviewer の指摘が書式ではなく、内容（重みの扱いなど）に集中している → **形式は sensor が、内容は reviewer が確認し、判断者が承認するかどうかを決める**

確認が終わったら、`/aidlc park`（中断）で終了して構いません。

<!-- trial -->
確認（**最重要。まだ確認できていない**）:
- [ ] `required-sections` がテンプレート `requirements.md` を参照したか（合格の audit 行だけでは判別できない場合は、AI-DLC 側で「requirements.md に対して required-sections はどのテンプレートを使った？」と質問する）
- [ ] 2 つ目の intent では既存のコードがあるため、Reverse Engineering が実行されるか（実行されると所要時間が延びる）
- [ ] AI エージェントが要件書を作成する際に、テンプレートを雛形として使ったか

アイデア: テンプレートにあえて見出しを 1 つ追加しておくと、`SENSOR_FAILED` → AI エージェントが自ら修正 → `SENSOR_PASSED` の流れが audit に記録され、sensor の効果を示せる。
<!-- /trial -->

---

## 6. 発展編（チュートリアルの外）

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
- [ ] `git clean -fdx` の後、doctor と `/aidlc` が正常に動作するか（`active-space` は `tutorial-baseline` の commit の時点から存在したが、gitignore の対象のため削除される。`default` に戻るだけのはず）
<!-- /trial -->

<!-- trial -->
---

## 試走メモ（所要時間）

| 手順 | 目安 | 試走 1 回目 | メモ |
|---|---|---|---|
| 1. 開始 | 1 分 | 0 分 | 初期化は 1 秒未満 |
| 2. Requirements Analysis | 9 分 | 9 分 | review 約 3 分 |
| 3-1. Code Generation + 前の stage に戻る | 20 分 | 21 分（3 分で戻る + Requirements Analysis やり直し 6 分 + Code Generation の再実行 11 分） | 再実行はコードの生成 6 分 + review 3 分 |
| 3-2. Build and Test | 2 分 | 6 分 | うち 4〜5 分はデプロイ関連の stage を除外するやり取り → 手順 1 で先に伝えて短縮 |
| 4. audit | 3 分 | - | |
| 小計（1〜4） | 35 分 | 36 分（1〜3 のみ） | |
| 5. テンプレート化 + 2 つ目の intent | 10 分 | - | 手順 5-2 は未試走 |
| 合計（1〜5） | 45 分 | - | |
<!-- /trial -->
