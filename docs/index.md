# ai-dlc-navigator

ai-dlc-navigator は、[AI-DLC](https://github.com/awslabs/aidlc-workflows)（AI-Driven Development Life Cycle）を初めて使う人を、その人の言語（日本語・英語など）で案内する Agent Skill です。このページの後半では、AI-DLC の考え方を実際に操作しながら学ぶチュートリアルを紹介します。

## Skill の紹介

ai-dlc-navigator は、次の 3 つの場面で利用者を支援します。

- **AI-DLC の概要と、その設計の理由**を説明する
- **使い方**（セットアップ、最初の `/aidlc` の実行、承認ゲートでの回答方法、操作に迷ったときの対処）を案内する
- **設定**（scope、depth、Guard Policy など）を、利用者の状況に合わせて提案する

AI-DLC のドキュメント一式を同梱しているため、AI-DLC のリポジトリを clone する必要はありません。

## インストール

[GitHub CLI](https://cli.github.com/) 2.100 以降が必要です（`gh skill` はプレビュー機能です）。

```bash
gh skill install icoxfog417/ai-dlc-navigator ai-dlc-navigator --agent claude-code --scope user
```

Skill は `~/.claude/skills/ai-dlc-navigator/` にインストールされ、すべてのプロジェクトで使用できます。AI-DLC 本体のインストール方法は、[AI-DLC の公式ドキュメント](https://github.com/awslabs/aidlc-workflows) を参照してください。

## 使い方

**新しい** Claude Code の会話を開始し（Skill は会話の開始時に読み込まれます）、自分の言葉で質問するか、Skill の名前を指定して呼び出します。

```text
AI-DLC とは？初めてなので、何から始めればいいですか？
/ai-dlc-navigator sensor と review の違いを教えて
```

- **navigator は説明を行い、判断と実行は利用者が行います。** navigator が利用者に代わって `/aidlc` の stage を進めたり、承認ゲートで回答したりすることはありません。navigator が自ら実行するのは `aidlc version` や `aidlc doctor` のような読み取り専用の確認だけで、それ以外のコマンドは提示するだけです
- **`aidlc config` を実行した後は、新しい会話を開始してください。** `/aidlc` と AI-DLC の hook は、会話の開始時に読み込まれます。新しい会話でも navigator は使えるため、作業を進めながら承認ゲートの意味などを質問できます

更新方法や、AI-DLC と併用する際の注意点は、[README](https://github.com/icoxfog417/ai-dlc-navigator#readme) を参照してください。

> [!NOTE]
> 生成 AI は誤った出力をすることがあります。navigator や AI-DLC が作成した成果物と、それにかかるコストは、使用する前に確認してください。

## AI-DLC 実践: チュートリアル

[**AI-DLC v2 の中核を学ぶ : 判断をルールとして蓄積し、検証に生かす（45 分）**](tutorial.md)

AI-DLC v2 の中心となる考え方を、小さな CLI アプリケーションの作成を通じて体験します。人間（判断者）が下した判断は、AI-DLC によってルールとして保存され、次の作業ではそのルールに沿っているかが検査されます。途中で承認ゲートの意味などが分からない場合は、navigator に質問しながら進められます。

- 判断と学習: reviewer（AI-DLC の LLM エージェント）の指摘を受けて、判断者が AI エージェントに修正を指示し、その指示内容が `memory` にルールとして保存される
- 前の stage に戻る: 誤った判断に気づいたら、前の stage に戻ってやり直す
- 検証: 判断者がルールを要件書のテンプレートとして配置すると、sensor が LLM を使わないプログラムで、要件書がルールに沿っているかを検査する
- 記録: これらの経過は、すべて `audit` に記録される
