# ai-dlc-navigator

[AI-DLC](https://github.com/awslabs/aidlc-workflows)（AI-Driven Development Life Cycle）を初めて使う人を、その人の言語（日本語・英語など）で案内する Agent Skill です。後半では、AI-DLC の考え方を手を動かして学ぶチュートリアルを紹介します。

## Skill の紹介

ai-dlc-navigator は、次の 3 つを手伝います。

- **AI-DLC とは何か、なぜそう作られているか**を説明する
- **使い方**（セットアップ、最初の `/aidlc`、ゲートへの答え方、詰まったときの対処）を案内する
- **設定の選び方**（scope、depth、Guard Policy など）を状況に合わせて勧める

AI-DLC のドキュメント一式を同梱しているので、AI-DLC のリポジトリを clone する必要はありません。

## インストール

[GitHub CLI](https://cli.github.com/) 2.100 以降が必要です（`gh skill` はプレビュー機能です）。

```bash
gh skill install icoxfog417/ai-dlc-navigator ai-dlc-navigator --agent claude-code --scope user
```

`~/.claude/skills/ai-dlc-navigator/` に入り、どのプロジェクトでも使えるようになります。AI-DLC 本体のインストールは [AI-DLC の公式ドキュメント](https://github.com/awslabs/aidlc-workflows) を参照してください。

## 使い方

**新しい** Claude Code の会話を始めて（Skill は会話の開始時に読み込まれます）、自分の言葉で聞くか、Skill の名前で呼び出します。

```text
AI-DLC とは？初めてなので、何から始めればいいですか？
/ai-dlc-navigator sensor と review の違いを教えて
```

- **navigator は説明し、決めて実行するのはあなたです。** `/aidlc` の stage を代わりに進めたり、承認ゲートに代わりに答えたりはしません。自分で実行するのは `aidlc version` や `aidlc doctor` のような読み取りだけの確認で、それ以外のコマンドは提示するだけです
- **`aidlc config` の後は、新しい会話を始めてください。** `/aidlc` と AI-DLC の hook は会話の開始時に読み込まれます。新しい会話でも navigator は使えるので、作業しながらゲートの意味などを聞けます

更新方法や、AI-DLC と一緒に使うときの注意は [README](https://github.com/icoxfog417/ai-dlc-navigator#readme) を参照してください。

> [!NOTE]
> 生成 AI は間違えることがあります。navigator や AI-DLC が作ったものとコストは、使う前に確認してください。

## AI-DLC 実践: チュートリアル

[**判断が学習され、検証になるまで（45 分）**](tutorial.md)

AI-DLC v2 の中心にある「人の判断が学習され、次の作業で検証として使えるようになる」流れを、小さな CLI を 1 つ作りながら体験します。途中で「このゲートは何？」と思ったら、navigator に聞きながら進められます。

- reviewer の指摘を見て人が直し、その判断が `memory` のルールになる
- 間違った判断に気づいて、前の stage に戻ってやり直す
- ルールをテンプレートに格上げし、sensor に決定的に確かめさせる
- そのすべてが `audit` に記録として残る
