# ai-dlc-navigator

[AI-DLC](https://github.com/awslabs/aidlc-workflows)（AI-Driven Development Life Cycle）を初めて使う人のための、Claude Code などで動く Agent Skill と、AI-DLC の考え方を手を動かして学ぶチュートリアルです。

## チュートリアル

[**判断が学習され、検証になるまで（45 分）**](tutorial.md)

AI-DLC v2 の中心にある「人の判断が学習され、次の作業で検証として使えるようになる」流れを、小さな CLI を 1 つ作りながら体験します。

- reviewer の指摘を見て人が直し、その判断が `memory` のルールになる
- 間違った判断に気づいて、前の stage に戻ってやり直す
- ルールをテンプレートに格上げし、sensor に決定的に確かめさせる
- そのすべてが `audit` に記録として残る

## ai-dlc-navigator（Skill）

AI-DLC を初めて使う人を、その人の言語（日本語・英語など）で案内する Agent Skill です。チュートリアルの途中で「このゲートは何？」「sensor って何？」と聞くときにも使えます。

- **AI-DLC とは何か、なぜそう作られているか**を説明する
- **使い方**（セットアップ、最初の `/aidlc`、ゲートへの答え方、詰まったときの対処）を案内する
- **設定の選び方**（scope、depth、Guard Policy など）を状況に合わせて勧める

AI-DLC のドキュメント一式を同梱しているので、AI-DLC のリポジトリを clone する必要はありません。

```bash
gh skill install icoxfog417/ai-dlc-navigator ai-dlc-navigator --agent claude-code --scope user
```

インストールすると、新しい Claude Code の会話で次のように使えます。

```text
AI-DLC とは？初めてなので、何から始めればいいですか？
/ai-dlc-navigator sensor と review の違いを教えて
```

更新方法や、AI-DLC と一緒に使うときの注意は [README](https://github.com/icoxfog417/ai-dlc-navigator#readme) を参照してください。

> [!NOTE]
> 生成 AI は間違えることがあります。navigator や AI-DLC が作ったものとコストは、使う前に確認してください。
