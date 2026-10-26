# AGENTS.md

## 仓库布局与权威源指向

- 仓库根即 Skill 本体：`SKILL.md` + `references/` + `scripts/` + `agents/openai.yaml` 是 Skill 内容；`README.md` / `README.zh-CN.md` / `LICENSE` 为发布配套。
- 本仓库是公开发布副本；维护者的本地权威源在私有同步目录中，对外只看本仓库与修复 PR/直接提交。

## 硬约束

- **身份**：所有 commit 用 `x0c <x0c@users.noreply.github.com>`（author 与 committer 同设置），不得出现真实姓名邮箱。
- **隐私**：禁止出现公司/组织名、内网地址、真实域名、个人标识、手机号（推送前敏感词扫描）。
- **语言**：`SKILL.md` / `references/` / `scripts/` 用英文；README 中英双语（英文在前）。
- **验证**：改 `scripts/audit.py` 后先跑 `python3 scripts/test_audit.py`；改 `SKILL.md` / `references/` 的判据后，在一个真实 AGENTS.md 文档上跑一次 audit 并人工复核保留/删除/合并的裁定是否仍成立——audit 的干净结果只覆盖链接与结构，不证明规则语义被保留。

## 文档导航

| 文档 | 何时读 |
|---|---|
| `SKILL.md` | 审阅、修订或压缩 AGENTS.md 类指令文档时必读 |
| `references/decision-criteria.md` | 裁定一条指令「保留 / 删除 / 合并」时对照判据 |
| `references/audit.md` | 使用 audit 脚本、解读其报告输出时 |
| `scripts/audit.py` | 链接与结构只读审计工具本体（含 JSON 模式） |
