# AI-DLC v2 チュートリアル（試走版）: 判断が学習され、検証になるまで

> 所要時間: **45 分**（本編 約 35 分 + 続き 約 10 分。準備は含まない）
>
> 状態: **試走用ドラフト（試走 1 回目を反映済み）**。AI-DLC 2.11.4 / Claude Code / `aidlc-playground`。
> 各手順の「確認」欄は試走で埋め、本番版では参加者向けの説明に置き換える。

## このチュートリアルで体験すること

人が下した**判断**が、

1. reviewer の指摘を見て人が直す（判断）
2. `memory/project.md` のルールになる（学習）
3. テンプレートに格上げすると sensor が決定的に確かめる（検証）
4. 次の作業では最初から守られ、reviewer は中身に集中できる

そして、そのすべてが `audit/` に残ること。途中で**間違った判断に気づいて stage を戻る**ことも体験する。

```
人の判断 ─▶ memory（約束） ─▶ agent が最初から守る
    │            └─(人が格上げ)─▶ templates ─▶ sensor が確かめる
    └──────────── すべて audit に残る
```

用語の言い分け（混同しやすいので本文でも統一する）:

| 言葉 | 意味 |
|---|---|
| review の強さ `advisory` / `adversarial` | reviewer（LLM）が 1 回見るか、何周も反論と修正を繰り返すか |
| sensor の扱い `advisory` / `blocking` | 決定的なチェックの結果を伝えるだけか、ゲートを止めるか |
| memory | 守るもの（ルール・書式）。やり取りから学習され、手でも編集できる |
| knowledge | 参考にする資料。ファイルを持ち込む（今回は使わない） |

題材: **割り勘 CLI（TypeScript / Node.js）**

時間配分（試走 1 回目の実測に基づく）:

| パート | 内容 | 目安 |
|---|---|---|
| 本編 | 手順 1〜5（判断・学習・戻る・audit） | 約 35 分 |
| 続き | 手順 6（格上げと 2 本目の intent） | 約 10 分 |
| 合計 | | **45 分**（試走 1 回目からの見積もり） |

---

## 0. 準備（45 分の外。事前に済ませる）

ターミナルで（Claude Code の外で）実行する:

```bash
cd ~/aidlc-workspace/aidlc-playground
git init
aidlc config --harness claude          # 質問には推奨デフォルト（選択肢 1）
aidlc doctor                           # 「Project runtime stamp」の警告が出たら aidlc config をもう一度
git add -A && git commit -m "tutorial baseline" && git tag tutorial-baseline
```

- `aidlc config` はプロジェクトにファイルを書き込む（試走前の dry-run: `create=351 conflict=0`、既存ファイルの上書きなし）
- マシン側の AI-DLC が更新されていると、プロジェクトのバージョンとずれて doctor が警告を出す。**baseline をコミットする前に**揃える
- doctor の「hooks have not run」と「uncommitted change(s)」の警告は、この時点では正常
- 終わったら **playground で新しい Claude Code の会話を始める**（`/aidlc` と hook は会話の開始時に読み込まれる）

---

## 1. 開始（〜1 分）

```text
/aidlc express --review advisory --learnings on --sensors on 割り勘CLIをTypeScriptで作りたい。合計金額と人数を渡すと1人あたりの金額を出す。デプロイや監視は不要
```

- `express` の既定は reviewer・sensors・learnings がすべて off。フラグで 3 つとも on にする
- `--review advisory`: reviewer に 1 回だけ見てもらい、指摘を並べる（時間内に収めるため `adversarial` にはしない）
- 「デプロイや監視は不要」と最初に伝えておく。言わないと Build and Test の途中で deploy 系の stage（Deployment Pipeline / Deployment Execution / Observability Setup）を外すか聞かれ、4〜5 分かかる（試走 1 回目）
- 新規プロジェクトなので Reverse Engineering はスキップされる

確認:
- [x] 4 つのフラグを 1 行で受け付けた（`aidlc-state.md` に Review Override = advisory、Sensors / Learnings = on (set by you)）
- [ ] 「デプロイや監視は不要」で、最初から deploy 系が plan から外れるか

---

## 2. Requirements Analysis: 判断と学習（〜9 分）

1. 回答方法は **Guide me**（1 問ずつチャットで答える）を選ぶ
2. 質問に答える。**端数の扱いを聞かれたら、わざと「切り捨て」を選ぶ**（手順 3 の伏線）。聞かれなければ、自分から「端数は切り捨てで」と伝える
3. 成果物が書かれると sensor（advisory）→ review（product lead）の順に動く（review は 3 分ほどかかる）
4. reviewer の指摘（ID 付き）を見て、書式を指示する:

   ```text
   要件書には必ず「## 受け入れ条件」の節を設けて、各 FR の受け入れ条件を Given/When/Then で書いてください
   ```

5. **「Keep that for next time?」** と聞かれたら → **Yes, for this project**
6. 承認ゲートが開いたら **Approve**

見どころ:
- reviewer は相談相手。指摘が残っていても人は承認できる（受け入れたリスクとして記録される）
- 学習したルールは `aidlc/spaces/default/memory/project.md` の `## Corrections` に追記される → 開いて見る

```bash
tail -n 3 aidlc/spaces/default/memory/project.md
```

試走 1 回目で入った行:

```text
- 要件書（requirements.md）には必ず「## 受け入れ条件」の節を設け、各 FR の受け入れ条件を Given/When/Then で書く。 (learned 2026-11-13) <!-- cid:... -->
```

うまく聞かれなかったときの保険: 「承認。次からは要件書に受け入れ条件の節を必ず入れて」と言うと、質問なしで保存され、保存先が 1 行で表示される。

確認:
- [x] 「Keep that for next time?」が出た（audit では `DECISION_RECORDED`、Question Kind = learnings-note）
- [x] `project.md` に `(learned 2026-11-13)` 付きの行が入った（`RULE_LEARNED`）
- [x] 承認ゲートより前に指示したので、差し戻し（`GATE_REJECTED`）は発生しなかった。ゲートで Request Changes を選ぶやり方でも同じように学習されるはず（未確認）

---

## 3. Code Generation: stage を戻る（〜20 分）

1. Approve すると Construction の Code Generation に進む。express は plan の承認が off なので、plan の内容が 1 行表示されてすぐにコード生成が始まる
2. **その 1 行か、要件書を見直して「切り捨てだと合計が合わない（3000 円 ÷ 7 人 = 428 円 × 7 = 2996 円）」と気づいたら、すぐに戻る**:

   ```text
   /aidlc --stage requirements-analysis
   ```

   コード生成が終わるのを待たずに戻ると、1 回分（約 7 分）を節約できる（試走 1 回目は開始 3 分で戻った）

3. 既存のファイルについて Keep / Modify / Redo を聞かれたら **Modify** を選び、「端数は幹事が負担する」に直す
4. Requirements をもう一度承認 → Code Generation がやり直しになる。今度は最後まで進め、architecture reviewer の review を見て Approve する（生成と review で約 11 分）

見どころ:
- 戻ってもファイルは消えない（Keep / Modify / Redo を選べる）。工程を戻れるので、ウォーターフォールではない
- 手順 2 で学習したルールは、やり直した Requirements にも最初から効いている

確認:
- [x] 戻った記録は `STAGE_JUMPED`（`Direction: BACKWARD`。やり直しで無効になった後続の成果物も記録される）
- [x] Modify を選んだ記録は `ARTIFACT_REUSED`（Decision: modify）

---

## 4. Build and Test → 完了（〜2 分）

- テストが実行される。結果を見て Approve すると intent が完了する（`WORKFLOW_COMPLETED`）

---

## 5. audit で履歴を見る（〜3 分）

```text
/aidlc --status
/aidlc-replay
```

```bash
# どんなイベントが何回あったか
grep -h '^\*\*Event\*\*' aidlc/spaces/default/intents/*/audit/*.md | sort | uniq -c | sort -rn
# 学習・戻る・Modify の記録
grep -n -A8 'RULE_LEARNED\|STAGE_JUMPED\|ARTIFACT_REUSED' aidlc/spaces/default/intents/*/audit/*.md
# sensor がどの stage で何回合格したか
grep -h -A6 'SENSOR_PASSED' aidlc/spaces/default/intents/*/audit/*.md | grep -E 'Sensor ID|Stage slug' | paste - - | sort | uniq -c
```

見るイベント:

| イベント | 意味 |
|---|---|
| `DECISION_RECORDED` / `QUESTION_ANSWERED` | 人に聞いた質問と、その答え（Keep の質問を含む） |
| `RULE_LEARNED` | ルールを学習した記録（保存先と見出し付き） |
| `REVIEW_REQUESTED` / `REVIEW_COMPLETED` | reviewer の review を頼んだ / 終わった記録 |
| `STAGE_JUMPED` | stage を戻った記録 |
| `ARTIFACT_REUSED` | 戻った先で既存のファイルを Keep / Modify した記録 |
| `SENSOR_FIRED` / `SENSOR_PASSED` / `SENSOR_FAILED` | sensor の結果 |
| `GATE_APPROVED` / `GATE_REJECTED` | 承認 / 差し戻し |
| `RECOMPOSED` | plan から stage を外した / 足した記録 |
| `CHANGE_ACCEPTED` | review の後にファイルが変わったことを検知し、そのまま進めた記録（試走 1 回目では `.gitignore`） |

**sensor は「見えない」のが普通**: 合格した結果はゲートで報告されない（報告されるのは指摘が残っている場合だけ）。動いたことは audit で確かめる（試走 1 回目では `required-sections` / `upstream-coverage` / `traceability` が 26 回動き、26 回とも合格）。

開始時にフラグで設定を変えた場合、`CEREMONY_SET` / `REVIEW_CLASS_CHANGED` は出ない。設定は `aidlc-state.md` に `set by you` として残る。

---

## 6. 学習を検証に格上げし、次の作業で確かめる（続き: 約 10 分）

### 6-1. ルールをテンプレートにする（人が判断して格上げする）

手順 2 のルール（受け入れ条件の節）を、`memory/templates/` に要件書のテンプレートとして置く。こうすると、同梱の `required-sections` sensor が見出しを決定的にチェックする（自作の sensor は不要）。

```text
memory/project.md の「受け入れ条件」のルールを、要件書のテンプレートとして aidlc/spaces/default/memory/templates/ に置いてください。見出しは今回の要件書に合わせて
```

- 試走 1 回目では `aidlc/spaces/default/memory/templates/requirements.md` が作られた（成果物 `requirements.md` と同じ名前。見出しは `## 出典` / `## 1. 意図の分析` / `## 2. 機能要件` / `## 受け入れ条件` …）

### 6-2. 2 本目の intent で確かめる

```text
/aidlc express --review advisory --learnings on --sensors on 割り勘CLIに、人ごとに重みを付ける傾斜配分を追加したい。デプロイや監視は不要
```

Requirements Analysis の承認ゲートまで進めて、次の 3 つを見る:

1. 何も言わなくても `## 受け入れ条件` が入っている → **memory（約束）が効いた**
2. `required-sections` が `SENSOR_PASSED` → **sensor が確かめた**
3. reviewer の指摘が書式ではなく中身（重みの扱いなど）に向いている → **形式は機械、中身は reviewer、判断は人**

見終わったら `/aidlc park`（中断）でよい。

確認（**最重要。まだ確かめられていない**）:
- [ ] `required-sections` がテンプレート `requirements.md` を見つけたか（合格の audit 行だけでは分からない場合は、AI-DLC 側で「requirements.md に対して required-sections はどのテンプレートを使った？」と聞く）
- [ ] 2 本目は既存のコードがあるので、Reverse Engineering が走るか（走ると時間が延びる）
- [ ] agent がテンプレートを書くときの雛形として使ったか

アイデア: テンプレートにわざと見出しを 1 つ足しておくと、`SENSOR_FAILED` → agent が自分で直す → `SENSOR_PASSED` の流れが audit に残り、sensor が効いたところを見せられる。

---

## 7. 発展編（チュートリアルの外）

- **間違った学習を直す**: `project.md` の学習行を手で消す。ルールは消えるが、`RULE_LEARNED` は audit に残る（ルールは人が直せる、記録は消えない）
- **ゲートを止める sensor**: 「金額に浮動小数を使わない」を自作 sensor（`default_severity: blocking` + `fire_on: gate`）にして、Fix findings / Override blocking sensors を体験する。learning loop が作る雛形は `fire_on` を書かず、チェック本体も手書きになる点に注意

---

## リセット（もう一度最初から）

harness を閉じてから:

```bash
cd ~/aidlc-workspace/aidlc-playground
git reset --hard tutorial-baseline
git clean -ndx           # 消えるものを先に確認（何も消さない）
git clean -fdx
aidlc doctor
```

- `-x` が必要: AI-DLC の実行時ファイル（`aidlc/.aidlc-sessions/`、`intents/.aidlc-engine/`、`runtime-graph.json`、`active-intent` など）と `node_modules/`・`dist/` は gitignore されているため、`git clean -fd` では残る（試走 1 回目で確認）
- `-x` を付けると、baseline の時点からあった `aidlc/active-space`（どの space を使っているかの記録）も消える。消えても `default` に戻るだけのはずだが、リセット後に doctor で確認する
- intent だけやり直すなら `/aidlc intent archive <name>` でもよい。ただし **memory（学習したルール・テンプレート）は intent の外にあるので残る**
- 新しい Claude Code の会話を始める

確認:
- [ ] `git clean -fdx` の後、doctor と `/aidlc` が普通に動くか

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
