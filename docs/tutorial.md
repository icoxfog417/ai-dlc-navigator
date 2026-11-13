# 判断が学習され、検証になるまで（45 分）

AI-DLC v2 の中心にある考え方を、小さな CLI を 1 つ作りながら体験するチュートリアルです。

> [!NOTE]
> **所要時間**
>
> 45 分（本編 約 35 分 + 続き 約 10 分）。準備の時間は含みません。
> AI-DLC 2.11.4 と Claude Code で確認しています。

<!-- trial -->
> 状態: **試走用ドラフト（試走 1 回目を反映済み）**。trial の目印（HTML コメント）で囲んだ部分は試走用のメモで、GitHub Pages のサイトには出ません。
<!-- /trial -->

## このチュートリアルで体験すること

人が下した**判断**が、次のように育っていきます。

1. reviewer の指摘を見て、人が直す（判断）
2. 直した内容が `memory/project.md` のルールになる（学習）
3. ルールをテンプレートに格上げすると、sensor が決定的に確かめる（検証）
4. 次の作業ではルールが最初から守られ、reviewer は中身に集中できる

そして、そのすべてが `audit/` に記録として残ります。途中で、**間違った判断に気づいて stage を戻る**ことも体験します。

```text
人の判断 ─▶ memory（約束） ─▶ agent が最初から守る
    │            └─(人が格上げ)─▶ templates ─▶ sensor が確かめる
    └──────────── すべて audit に残る
```

### 用語の言い分け

AI-DLC では同じ `advisory` という言葉が 2 か所で別の意味に使われます。このチュートリアルでは次のように言い分けます。

| 言葉 | 意味 |
|---|---|
| review の強さ `advisory` / `adversarial` | reviewer（LLM）が 1 回だけ見るか、反論と修正を何周も繰り返すか |
| sensor の扱い `advisory` / `blocking` | 決定的なチェックの結果を伝えるだけか、ゲートを止めるか |
| memory | 守るもの（ルール・書式）。やり取りから学習され、手でも編集できる |
| knowledge | 参考にする資料。ファイルを持ち込む（今回は使わない） |

### 題材と時間配分

題材は **割り勘 CLI（TypeScript / Node.js）** です。

| パート | 内容 | 目安 |
|---|---|---|
| 本編 | 手順 1〜5（判断・学習・戻る・audit） | 約 35 分 |
| 続き | 手順 6（格上げと 2 本目の intent） | 約 10 分 |
| 合計 | | **45 分** |

---

## 0. 準備（45 分の外。事前に済ませる）

### 必要なもの

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
- AI-DLC（`aidlc` コマンド）。インストール方法は [AI-DLC の公式ドキュメント](https://github.com/awslabs/aidlc-workflows) を参照してください
- Node.js と git

### 練習用のプロジェクトを作る

ターミナル（Claude Code の外）で、空のフォルダを作って AI-DLC をセットアップします。

```bash
mkdir ~/aidlc-playground && cd ~/aidlc-playground
git init
aidlc config --harness claude          # 質問には推奨デフォルト（選択肢 1）を選ぶ
aidlc doctor
git add -A && git commit -m "tutorial baseline" && git tag tutorial-baseline
```

最後の行で、今の状態を `tutorial-baseline` という基準点として残しています。[リセット](#リセットもう一度最初から) のときに、この基準点まで戻せます。

> [!TIP]
> **doctor の警告について**
>
> - 「Project runtime stamp」の警告が出たら、マシン側の AI-DLC が更新されてプロジェクトとバージョンがずれています。`aidlc config --harness claude` をもう一度実行して揃えてから、基準点をコミットしてください
> - 「hooks have not run」と「uncommitted change(s)」の警告は、この時点では正常です

終わったら、**このフォルダで新しい Claude Code の会話を始めてください**。`/aidlc` と hook は、会話の開始時に読み込まれます。

<!-- trial -->
試走メモ: 試走前の dry-run は `create=351 conflict=0`（既存ファイルの上書きなし）。
<!-- /trial -->

---

## 1. 開始（約 1 分）

Claude Code で次のように入力します。

```text
/aidlc express --review advisory --learnings on --sensors on 割り勘CLIをTypeScriptで作りたい。合計金額と人数を渡すと1人あたりの金額を出す。デプロイや監視は不要
```

- `express` は一番軽い進め方（scope）です。既定では reviewer・sensors・learnings がすべて off なので、フラグで 3 つとも on にします
- `--review advisory` は、reviewer に 1 回だけ見てもらい、指摘を並べてもらう設定です。時間内に収めるため、何周も繰り返す `adversarial` にはしません
- 「デプロイや監視は不要」と最初に伝えておきます。言わないと、Build and Test の途中で deploy 系の stage を外すかどうか聞かれ、数分かかります
- 新しいプロジェクトなので、既存コードの解析（Reverse Engineering）はスキップされます

<!-- trial -->
確認:
- [x] 4 つのフラグを 1 行で受け付けた（`aidlc-state.md` に Review Override = advisory、Sensors / Learnings = on (set by you)）
- [ ] 「デプロイや監視は不要」で、最初から deploy 系が plan から外れるか（試走 1 回目は言わなかったため、Build and Test で外すやり取りに 4〜5 分かかった）
<!-- /trial -->

---

## 2. Requirements Analysis: 判断と学習（約 9 分）

1. 回答方法は **Guide me**（1 問ずつチャットで答える）を選びます
2. 質問に答えます。**端数の扱いを聞かれたら、わざと「切り捨て」を選んでください**（手順 3 の伏線です）。聞かれなければ、自分から「端数は切り捨てで」と伝えます
3. 要件書が書かれると、sensor → reviewer（product lead）の順に動きます。reviewer の確認には 3 分ほどかかります
4. reviewer の指摘（ID 付き）を見て、書式を指示します。

    ```text
    要件書には必ず「## 受け入れ条件」の節を設けて、各 FR の受け入れ条件を Given/When/Then で書いてください
    ```

5. **「Keep that for next time?」**（次回も使うか）と聞かれたら、**Yes, for this project** を選びます
6. 承認ゲートが開いたら **Approve** します

学習したルールは `memory/project.md` の `## Corrections` に追記されます。開いて確認してみましょう。

```bash
tail -n 3 aidlc/spaces/default/memory/project.md
```

次のような行が入っているはずです。

```text
- 要件書（requirements.md）には必ず「## 受け入れ条件」の節を設け、各 FR の受け入れ条件を Given/When/Then で書く。 (learned 2026-11-13) <!-- cid:... -->
```

> [!TIP]
> **見どころ**
>
> - reviewer は相談相手です。指摘が残っていても、人は承認できます（受け入れたリスクとして記録されます）
> - 直した内容が、その場限りではなく「次回からのルール」として残ります

> [!NOTE]
> **「Keep that for next time?」が出なかったら**
>
> 「承認。次からは要件書に受け入れ条件の節を必ず入れて」と伝えてください。質問なしでルールとして保存され、保存先が 1 行で表示されます。

<!-- trial -->
確認:
- [x] 「Keep that for next time?」が出た（audit では `DECISION_RECORDED`、Question Kind = learnings-note）
- [x] `project.md` に `(learned 2026-11-13)` 付きの行が入った（`RULE_LEARNED`）
- [x] 承認ゲートより前に指示したので、差し戻し（`GATE_REJECTED`）は発生しなかった。ゲートで Request Changes を選ぶやり方でも同じように学習されるはず（未確認）
<!-- /trial -->

---

## 3. Code Generation: stage を戻る（約 20 分）

1. Approve すると、Construction の Code Generation に進みます。`express` ではコードの計画（plan）を承認する手順が省かれていて、計画が 1 行表示されたらすぐにコード生成が始まります
2. **その 1 行か要件書を見て、「切り捨てだと合計が合わない」と気づいたら、すぐに戻ります**（3000 円 ÷ 7 人 = 428 円で、428 円 × 7 = 2996 円にしかなりません）

    ```text
    /aidlc --stage requirements-analysis
    ```

    コード生成が終わるのを待たずに戻ると、1 回分（約 7 分）を節約できます。

3. 既存のファイルをどうするか（Keep / Modify / Redo）聞かれたら **Modify** を選び、「端数は幹事が負担する」に直します
4. Requirements をもう一度承認すると、Code Generation がやり直しになります。今度は最後まで進め、architecture reviewer の指摘を見てから Approve します（生成と review で約 11 分）

> [!TIP]
> **見どころ**
>
> - 戻ってもファイルは消えません。Keep / Modify / Redo から選べます。工程を戻れるので、ウォーターフォールではありません
> - 手順 2 で学習したルールは、やり直した Requirements にも最初から効いています

<!-- trial -->
確認:
- [x] 戻った記録は `STAGE_JUMPED`（`Direction: BACKWARD`。やり直しで無効になった後続の成果物も記録される）
- [x] Modify を選んだ記録は `ARTIFACT_REUSED`（Decision: modify）
- 試走 1 回目はコード生成の開始 3 分で戻った
<!-- /trial -->

---

## 4. Build and Test → 完了（約 2 分）

テストが実行されます。結果を見て Approve すると、この作業（intent）は完了です。

---

## 5. audit で履歴を見る（約 3 分）

ここまでのやり取りが、どう記録されたかを見ます。まず Claude Code で次を入力します。

```text
/aidlc --status
/aidlc-replay
```

続けてターミナルで、記録そのもの（audit）を確認します。

```bash
# どんなイベントが何回あったか
grep -h '^\*\*Event\*\*' aidlc/spaces/default/intents/*/audit/*.md | sort | uniq -c | sort -rn
# 学習・戻る・Modify の記録
grep -n -A8 'RULE_LEARNED\|STAGE_JUMPED\|ARTIFACT_REUSED' aidlc/spaces/default/intents/*/audit/*.md
# sensor がどの stage で何回合格したか
grep -h -A6 'SENSOR_PASSED' aidlc/spaces/default/intents/*/audit/*.md | grep -E 'Sensor ID|Stage slug' | paste - - | sort | uniq -c
```

注目するイベント:

| イベント | 意味 |
|---|---|
| `DECISION_RECORDED` / `QUESTION_ANSWERED` | 人に聞いた質問と、その答え（「Keep that for next time?」を含む） |
| `RULE_LEARNED` | ルールを学習した記録（保存先と見出し付き） |
| `REVIEW_REQUESTED` / `REVIEW_COMPLETED` | reviewer に確認を頼んだ / 確認が終わった記録 |
| `STAGE_JUMPED` | stage を戻った記録 |
| `ARTIFACT_REUSED` | 戻った先で、既存のファイルを Keep / Modify した記録 |
| `SENSOR_FIRED` / `SENSOR_PASSED` / `SENSOR_FAILED` | sensor が動いた / 合格 / 不合格 |
| `GATE_APPROVED` / `GATE_REJECTED` | 承認 / 差し戻し |
| `RECOMPOSED` | plan から stage を外した / 足した記録 |
| `CHANGE_ACCEPTED` | review の後にファイルが変わったことを検知し、そのまま進めた記録 |

> [!NOTE]
> **sensor は「見えない」のが普通です**
>
> 合格した結果は、ゲートでは報告されません。報告されるのは、指摘が残っている場合だけです。sensor が動いたことは audit で確かめます（`required-sections` / `upstream-coverage` / `traceability` が何十回も動いているはずです）。

> [!NOTE]
> **設定変更の記録について**
>
> 手順 1 のように開始時にフラグで設定した場合、設定変更のイベント（`CEREMONY_SET` / `REVIEW_CLASS_CHANGED`）は出ません。設定は `aidlc-state.md` に `set by you` として残ります。

<!-- trial -->
試走 1 回目: sensor は 26 回動いて 26 回とも合格。`CHANGE_ACCEPTED` は `.gitignore`（コード生成が `node_modules/` と `dist/` を追記した）。
<!-- /trial -->

---

## 6. 学習を検証に格上げし、次の作業で確かめる（続き: 約 10 分）

> [!WARNING]
> **この手順はまだ検証中です**
>
> 手順 6-2 は試走で確認できていません。結果が説明と違ったら、[Issue](https://github.com/icoxfog417/ai-dlc-navigator/issues) で教えてください。

### 6-1. ルールをテンプレートにする

手順 2 のルール（受け入れ条件の節）を、`memory/templates/` に要件書のテンプレートとして置きます。こうすると、AI-DLC に同梱されている `required-sections` という sensor が、要件書の見出しが揃っているかを決定的にチェックするようになります。自分で sensor を作る必要はありません。

ルールをチェックに格上げするかどうかも、人が判断します。Claude Code で次のように頼みます。

```text
memory/project.md の「受け入れ条件」のルールを、要件書のテンプレートとして aidlc/spaces/default/memory/templates/ に置いてください。見出しは今回の要件書に合わせて
```

`aidlc/spaces/default/memory/templates/requirements.md` が作られます。ファイル名は成果物の `requirements.md` と同じです。

### 6-2. 2 本目の intent で確かめる

```text
/aidlc express --review advisory --learnings on --sensors on 割り勘CLIに、人ごとに重みを付ける傾斜配分を追加したい。デプロイや監視は不要
```

Requirements Analysis の承認ゲートまで進めて、次の 3 つを見ます。

1. 何も言わなくても `## 受け入れ条件` が入っている → **memory（約束）が効いた**
2. `required-sections` が `SENSOR_PASSED` になっている → **sensor が確かめた**
3. reviewer の指摘が書式ではなく、中身（重みの扱いなど）に向いている → **形式は機械、中身は reviewer、判断は人**

見終わったら `/aidlc park`（中断）で終えて構いません。

<!-- trial -->
確認（**最重要。まだ確かめられていない**）:
- [ ] `required-sections` がテンプレート `requirements.md` を見つけたか（合格の audit 行だけでは分からない場合は、AI-DLC 側で「requirements.md に対して required-sections はどのテンプレートを使った？」と聞く）
- [ ] 2 本目は既存のコードがあるので、Reverse Engineering が走るか（走ると時間が延びる）
- [ ] agent がテンプレートを書くときの雛形として使ったか

アイデア: テンプレートにわざと見出しを 1 つ足しておくと、`SENSOR_FAILED` → agent が自分で直す → `SENSOR_PASSED` の流れが audit に残り、sensor が効いたところを見せられる。
<!-- /trial -->

---

## 7. 発展編（チュートリアルの外）

- **間違った学習を直す**: `project.md` の学習した行を手で消します。ルールは消えますが、`RULE_LEARNED` は audit に残ります。ルールは人が直せて、記録は消えません
- **ゲートを止める sensor**: 「金額に浮動小数を使わない」というチェックを自分で sensor として作り（`default_severity: blocking` と `fire_on: gate`）、不合格のときに Fix findings / Override blocking sensors を選ぶ体験をします。learning loop が作る雛形には `fire_on` が書かれず、チェック本体も自分で書く必要がある点に注意してください

---

## リセット（もう一度最初から）

Claude Code を閉じてから、ターミナルで実行します。

```bash
cd ~/aidlc-playground
git reset --hard tutorial-baseline
git clean -ndx           # 消えるものを先に確認する（何も消さない）
git clean -fdx
aidlc doctor
```

- `-x` が必要です。AI-DLC の実行時ファイル（`aidlc/.aidlc-sessions/`、`intents/.aidlc-engine/`、`runtime-graph.json` など）と `node_modules/`・`dist/` は git の管理外なので、`git clean -fd` では残ります
- `-x` を付けると、どの space を使っているかの記録（`aidlc/active-space`）も消えます。リセット後に `aidlc doctor` で問題がないか確認してください
- 作業（intent）だけやり直すなら `/aidlc intent archive <name>` でも構いません。ただし、**memory（学習したルールやテンプレート）は intent の外にあるので残ります**
- 終わったら、新しい Claude Code の会話を始めてください

<!-- trial -->
確認:
- [ ] `git clean -fdx` の後、doctor と `/aidlc` が普通に動くか（`active-space` は baseline の時点からあったが gitignore 対象なので消える。`default` に戻るだけのはず）
<!-- /trial -->

<!-- trial -->
---

## 試走メモ（所要時間）

| 手順 | 目安 | 試走 1 回目 | メモ |
|---|---|---|---|
| 1. 開始 | 1 分 | 0 分 | 初期化は 1 秒未満 |
| 2. Requirements | 9 分 | 9 分 | review 約 3 分 |
| 3. Code Generation + 戻る | 20 分 | 21 分（3 分で戻る + Requirements やり直し 6 分 + 再生成 11 分） | 再生成は生成 6 分 + review 3 分 |
| 4. Build and Test | 2 分 | 6 分 | うち 4〜5 分は deploy 系を外すやり取り → 手順 1 で先に伝えて短縮 |
| 5. audit | 3 分 | - | |
| 小計（1〜5） | 35 分 | 36 分（1〜4 のみ） | |
| 6. 格上げ + 2 本目 | 10 分 | - | 手順 6-2 は未試走 |
| 合計（1〜6） | 45 分 | - | |
<!-- /trial -->
