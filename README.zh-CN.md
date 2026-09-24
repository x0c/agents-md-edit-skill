**语言：** [English](README.md) | 简体中文

# agents-md

这是一个维护全局或项目 `AGENTS.md` 的 Agent skill。它按规则影响的决策聚簇，清除过时或容易重新获得的描述，并保留 Agent 在查阅文档索引之前就必须知道的约束。结构检查可以发现坏链接；规则含义仍需人工或协调 Agent 复核。

## 安装

安装工具需要 Node.js。下面一条命令可在 macOS、Linux 或 Windows 上为兼容的 Coding Agent 安装此 skill：

```sh
npx skills add x0c/agents-md-skill --skill agents-md -g -y
```

附带的审计脚本需要 Python 3；无需服务或付费 API。

## 使用

请你的 Coding Agent 调用 `agents-md`：

```text
Use the agents-md skill to review and compact this repository's AGENTS.md.
Read the whole file, preserve effective rules and exceptions, and check its document links.
```

也可以只要求修改一条规则，或进行只读评审。Skill 会区分局部修改与全文整理；运行环境支持时，会要求由专门的子代理执笔。

## 测试重点

- 同领域规则是否聚在一起，同时避免每条规则各占一个小章节？
- 原有禁令、例外和适用范围是否保留？
- 新 Agent 能否通过文档索引找到所需细节？
- 常驻上下文是否减少，同时不损害决策？

内附的 `scripts/audit.py` 只检查链接和结构；检查通过不代表规则含义完全正确。如果发现 skill 处理不当，请[提交 issue](https://github.com/x0c/agents-md-skill/issues)，附上脱敏后的改前改后示例，以及受影响的决策。

## 许可证

MIT，见 [LICENSE](LICENSE)。
