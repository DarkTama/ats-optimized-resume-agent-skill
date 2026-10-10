# ats-optimized-resume-agent-skill

[English](README.md) | **中文文档** | [安装指南](docs/INSTALL.md)

适用于 **PI-Desktop**、**Claude Code** 及 AI 编程助手的简历定制与精修技能。支持从零定制、局部微调、PDF/DOCX 简历母版解析、确定性 ATS 关键词评分，并生成符合 ATS 规范的高品质 Word 文档（`.docx`）与印刷级 PDF（`.pdf`）。

---

## ⚡ 快速安装

直接在终端或代理中运行对应系统的单条命令：

**Windows (PowerShell):**
```powershell
git clone https://github.com/DarkTama/ats-optimized-resume-agent-skill.git $env:TEMP\build-tailored-resume; & "$env:TEMP\build-tailored-resume\install.ps1" -Scope user
```

**macOS / Linux:**
```bash
git clone https://github.com/DarkTama/ats-optimized-resume-agent-skill.git /tmp/build-tailored-resume && chmod +x /tmp/build-tailored-resume/install.sh && /tmp/build-tailored-resume/install.sh --user
```

安装完成后，在 AI 编程助手中直接唤起：
- **PI-Desktop**: 在对话中直接说：`"帮我针对这个岗位定制简历"` 或 `"帮我修改简历"`
- **Claude Code**: 输入 `/build-tailored-resume`

*如需项目级安装、手动 pip 安装或离线环境配置，请查阅 [docs/INSTALL.md](docs/INSTALL.md)。*

---

## 核心功能

- **两种工作模式**：
  - **模式 A（全流程定制）**：输入简历母版 + 目标岗位 JD，自动分析、对齐关键词并去 AI 味改写。
  - **模式 B（靶向微调）**：快速微调局部子弹点、调整技能栈、压缩单页排版，无需重走全量采集流程。
- **多格式母版解析**：支持通过 `resume-skill extract` 自动提取 `.pdf`、`.docx`、`.md`、`.txt` 文本。
- **确定性 ATS 关键词评分**：通过 `resume-skill ats` 计算覆盖率，列出缺失关键词与章节分布，拒绝模型幻觉。
- **ATS 安全主题系统**：所有主题仅控制字体、颜色、间距和边框，绝不使用多栏布局或文本框，确保 100% 通过 ATS 机器解析。
- **双格式排版渲染**：一键生成排版精准的 Word 文档（`.docx`）与基于 RenderCV / Typst 的高清印刷级 PDF（`.pdf`）。

---

## 主题设计

所有主题均采用 ATS 安全的单栏排版与标准系统字体。

| 主题名称 | 适用领域 | 字体搭配 | 强调配色 | 分隔线样式 |
|---|---|---|---|---|
| `modern-clean` *(默认)* | 科技、互联网、产研 | Calibri / Source Sans 3 | 深海军蓝 (`#1F3864`) | 0.75pt 实线边框 |
| `executive-serif` | 金融、咨询、法律、管理层 | Georgia / XCharter | 深炭黑 (`#262626`) | 0.4pt 细线，居中标题 |
| `minimalist-mono` | 量化、底层开发、科研 | Arial / Roboto | 纯黑白 (`#000000`) | 极简留白（无分隔线） |

---

## 命令行工具 (`resume-skill`)

内置 CLI 提供完整的校验、评分、文本提取与渲染能力：

```bash
# 渲染生成 DOCX 或 PDF（支持主题）
resume-skill render --input tailored_resume.json --output resume.docx --theme modern-clean
resume-skill render --input tailored_resume.json --output resume.pdf --theme modern-clean

# 针对目标岗位 JD 进行 ATS 关键词覆盖率打分
resume-skill ats --resume tailored_resume.json --jd job_description.md

# 从已有简历文件提取纯文本
resume-skill extract --input master_resume.pdf --output master.txt

# 校验 JSON 格式及检测 AI 常见空话套话
resume-skill validate --input tailored_resume.json

# 导出 RenderCV YAML 配置
resume-skill export --input tailored_resume.json --output resume.yaml --theme modern-clean
```

---

## 质量把控流程

本技能严格遵循带质量门禁的七步防幻觉工作流：

| 阶段 | 核心任务 | 质量把控点 |
|---|---|---|
| **1. 信息录入** | 读取简历母版与目标 JD | 候选人信息及基础经历已确认 |
| **2. 岗位分析** | 提炼 JD 核心技能、硬性要求与关键词 | 确定优先匹配的关键词清单 |
| **3. 策略对齐** | 确定叙事策略、项目排序与经历侧重点 | 策略经用户确认 |
| **4. 简历定制** | 遵循“行动动词+工具+业务量化结果”改写 | 完成去 AI 痕迹检查 |
| **5. ATS 审查** | 执行确定性关键词覆盖率打分 | 覆盖率达标或核心词均有体现 |
| **6. 格式渲染** | 选择主题，渲染生成 `.docx` 与 `.pdf` | 模式校验通过，文件顺利输出 |
| **7. 交付核验** | 确认单页排版完整度、超链接有效性及真实度 | 最终交付成品 |

*详细规范详见 [SKILL.md](SKILL.md)。*

---

## 架构与设计决策

- [CONTEXT.md](CONTEXT.md): 领域模型与核心术语统一定义。
- [docs/adr/0001-themes-style-only.md](docs/adr/0001-themes-style-only.md): 架构决策记录（强制限定主题仅可修改样式，不可修改结构）。

---

## 许可证

MIT
