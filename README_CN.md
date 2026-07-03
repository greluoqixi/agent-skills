# Agent Skills

[English Version](./README.md)

Claude Code 和 Codex CLI 的 AI Agent 技能合集，以插件市场形式分发。

## 特性

### 智能代码库索引

生成结构化的 `CLAUDE.md` / `AGENTS.md` 文件作为 AI 的可导航索引。每个文件回答核心问题：哪些文件重要、入口在哪、模块如何关联。

- **10 种项目类型**：Python、Node/Web、Rust、Java、Go、基础设施、自动驾驶、机器人(ROS2)、嵌入式系统、通用兜底
- **4 阶段工作流**：Probe（检测类型）→ Scan（映射结构）→ Generate（生成文档）→ Verify（验证输出）
- **渐进式披露**：根文件作为导航枢纽（≤250 行），细节下沉到子目录文件，按需加载

### 基于清单的同步

生成的文件通过 `.claude/.claude-md-state.json` 或 `.codex/.agents-md-state.json` 追踪各 section 的 SHA-256 哈希。后续同步时，哈希匹配的 section 可安全重生成；哈希变化的 section 为用户手动修改，自动保留。不再覆盖人工调整。

### 多层维护防线

三层防御防止文档腐化：

| 层级 | 机制 | 原理 |
|------|------|------|
| **硬约束** | SessionStart hook | `check-stale.py` 指纹化目录结构；harness 在会话间检测到结构变化时注入 system-reminder |
| **软约束** | 自维护看门狗 | 每个生成的文件（根 + 所有子目录）都包含维护规则，指示 AI 在结构变更后同步 |
| **上下文约束** | 路径作用域规则 | `.claude/rules/`（Claude Code）和嵌套 `AGENTS.md`（Codex CLI）仅在 AI 进入匹配目录时加载 |

### 领域专用模板

- **自动驾驶**：Pipeline 架构（感知→预测→规划→控制），I/O topics，安全约束
- **机器人(ROS2)**：包级文档，节点/接口/参数/launch 文件
- **嵌入式系统**：CPS 分层架构，内存预算，时间约束，中断安全
- **标准软件**：Auth、DB、API 约定仅在无法从配置文件推断时才出现

## 市场安装

将本市场添加到你的 Agent：

**Claude Code：**

```bash
/plugin marketplace add greluoqixi/agent-skills
```

安装 Claude Code 插件：

```bash
/plugin install claude-md-generator@claude-skills
```

**Codex CLI：**

```bash
codex plugin add greluoqixi/claude-skills
```

安装 Codex 插件：

```bash
codex plugin add agents-md-generator@claude-skills
```

## 插件列表

| 插件 | 版本 | 平台 | 描述 |
|------|------|------|------|
| [claude-md-generator](./plugins/claude-md-generator/) | 2.0.0 | Claude Code | 生成并维护 CLAUDE.md 作为智能代码库索引。支持 10 种项目类型。包含 SessionStart hook 自动检测目录结构变化。 |
| [agents-md-generator](./plugins/agents-md-generator/) | 1.0.0 | Codex CLI | 为 Codex CLI 生成并维护 AGENTS.md 智能代码库索引。支持 10 种项目类型。包含漂移检测脚本，支持嵌套 AGENTS.md。 |

## 手动安装

如果不使用市场：

**Claude Code：**

```bash
# 克隆仓库
git clone https://github.com/greluoqixi/agent-skills.git

# 将技能软链接到 Claude Code
ln -s $(pwd)/agent-skills/plugins/claude-md-generator/skills/claude-md-generator \
  ~/.claude/skills/claude-md-generator
```

**Codex CLI：**

```bash
# 克隆仓库
git clone https://github.com/greluoqixi/agent-skills.git

# 将技能软链接到 Codex CLI
ln -s $(pwd)/agent-skills/plugins/agents-md-generator/skills/agents-md-generator \
  ~/.codex/skills/agents-md-generator
```

## 更新

刷新市场目录并将已安装的插件升级到最新版本：

**Claude Code：**

```bash
# 刷新市场目录
/plugin marketplace update

# 升级插件到最新版本
/plugin update claude-md-generator@claude-skills
```

如果 `update` 子命令不可用，则卸载后重装：

```bash
/plugin uninstall claude-md-generator
/plugin install claude-md-generator@claude-skills
```

**Codex CLI：**

```bash
# 刷新市场目录
codex plugin marketplace upgrade

# 重新添加插件获取最新版本
codex plugin add agents-md-generator@claude-skills
```

**手动安装（软链接）：**

```bash
cd ~/agent-skills && git pull
```

## 添加新插件

1. 在 `plugins/<name>/` 下创建插件结构
2. 添加清单文件：Claude Code 用 `.claude-plugin/plugin.json`，Codex CLI 用 `.codex-plugin/plugin.json`
3. 在 `plugins/<name>/skills/` 下添加技能
4. 在 `.claude-plugin/marketplace.json` 中注册
5. 提交并推送 — 用户通过 `/plugin marketplace update`（Claude Code）或 `codex plugin marketplace upgrade`（Codex CLI）获取更新

## 仓库结构

```
agent-skills/
├── .claude-plugin/
│   └── marketplace.json          # 市场注册表
├── plugins/
│   └── <plugin-name>/
│       ├── .claude-plugin/       # Claude Code 插件清单
│       │   └── plugin.json
│       ├── .codex-plugin/        # Codex CLI 插件清单
│       │   └── plugin.json
│       └── skills/
│           └── <skill-name>/
│               ├── SKILL.md
│               ├── scripts/
│               ├── references/
│               └── assets/
├── README.md
└── README_CN.md
```
