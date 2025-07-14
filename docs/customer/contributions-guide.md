## Contributions Guide
### How can I contribute?

There are multiple ways how you can help:

- 🐞 **Report a bug or request a feature**<br/>Go to the related repository and create a new issue for the bug/feature (go to `Issues` → `New Issue`).
- 🧑🏻‍💻 **Write code**<br/>Pick up an issue from [the board](https://github.com/orgs/SWP2025/projects/1) and continue reading this guide, if you want to send a pull request to one of our repositories.

### Sending Pull Request

Use English language everywhere on GitHub: in the code, comments, documentation, issues, PRs.

<details>
<summary>Why?</summary>

<br/>Most of us are Russian-speaking and we love Russian (🤍💙❤️), though we believe there are benefits of using English here:

1. **Bigger community:** there are many non-Russian speaking students studying and living in Innopolis, and everyone should be able to contribute.
2. **Open-source:** contributing to the global open-source community today is the crucial part of becoming a professional software engineer, and it's easier to so, if you use English.
3. Finally, practicing a foreign language has many benefits by itself (boosting brain activity, career benefits, etc.).
</details>

### Before you start

**For features:** before you start to work on a new feature, it's better to open a feature request issue first to discuss with the maintainers and other contributors whether the features is desired and decide on its design.
This can save time for everyone and help features to be deliveried faster.

**For small changes:** it's better to batch multiple typo fixes and small refactoring changes into one pull request to keep the commit history clean.

### Commit convention

We follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages, which allows the changelogs to be auto-generated.
Please read the guide if you aren't familiar with it already.

Note that `fix` and `feat` commit types are for **actual code changes that affect logic**.
If your commit changes docs or fixes typos, use `docs` or `chore` instead:

- <s>`fix: typo`</s> → `docs: fix typo`

### Creating pull request

> If you have troubles creating a pull request, [this guide](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) might help.

It's ok to have multiple commits in a single PR, you don't need to rebase or force push anything, because we will `Squash and Merge` the PR into one commit.

**Title**

Your title should also follow the Conventional Commits. An example of a good PR title would be:

```
feat: add animated snowfall background
```

**Description**

Make sure your PR have a clear description of the changes made and the reason behind them.
If your PR closes an existing issue (e.g. #123), make sure to mention it using [built-in GitHub functionality](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword), so it will be automatically closed once the PR gets merged:

```markdown
...

Fixes #123.
```