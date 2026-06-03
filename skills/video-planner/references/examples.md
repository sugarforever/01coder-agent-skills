# Video Script Skill Examples

## Example 1: User provides topic directly

**User**: 帮我写一期视频脚本，主题是用 Turborepo 管理 monorepo，面向前端开发者，大约6分钟

**Claude**: Confirms understanding, creates `./videos/2026-03-07-turborepo-monorepo/`, generates script.md, blog.md, youtube.md, and bilibili.md.

**script.md (excerpt)**:

```markdown
---
title: "Turborepo：让你的 monorepo 构建快 10 倍"
date: "2026-03-07"
duration: "~6 分钟"
platform: "YouTube / Bilibili"
---

# Turborepo：让你的 monorepo 构建快 10 倍

## Hook（0:00 - 0:10）

我的项目有 12 个包，完整构建从 8 分钟降到了 45 秒。

大家好我是 xxx，今天来聊聊 Turborepo - 它是怎么做到这件事的，以及你的项目该不该用它。

## 为什么 monorepo 构建这么慢（0:10 - 1:00）

先说问题。你有一个 monorepo，里面放了前端应用、组件库、工具函数、后端服务。改了一行代码，CI 把所有包全构建一遍。

其实大部分包根本没变。问题出在构建工具不知道包之间的依赖关系，只能全量跑。

## Turborepo 的核心思路（1:00 - 2:30）

Turborepo 做的事情很简单 - 它分析包之间的依赖图，只构建真正受影响的包。

再加上远程缓存，同一份代码在 CI 上构建过一次，你本地 pull 下来就不用再跑了。

（展示 turbo run build 的输出对比：全量 vs 增量）

## 上手配置（2:30 - 4:30）

我们直接来操作。

（录屏开始）

<!-- TODO: 补充实际安装和 turbo.json 配置步骤 -->

首先在项目根目录安装 Turborepo......

然后是 turbo.json 的配置......

## 实际效果（4:30 - 5:30）

（展示构建时间对比截图）

<!-- TODO: 补充实际数据 -->

## 收尾（5:30 - 6:00）

Turborepo 不是银弹，小项目没必要上。但如果你的 monorepo 已经开始因为构建速度拖慢开发效率，它值得试一下。

好了今天的分享就到这里，感谢大家收看，我们下期再见。
```

**youtube.md (excerpt)**:

```markdown
# YouTube 发布素材

## 标题

Turborepo：让你的 monorepo 构建快 10 倍

## 标题备选

- monorepo 构建太慢？Turborepo 帮你解决
- 告别全量构建：Turborepo 实战

## 描述

#turborepo #monorepo #前端工程化 #vercel

{产品推广链接}

monorepo 项目构建越来越慢？Turborepo 通过依赖图分析和远程缓存，只构建真正变化的包。这期视频从原理到实操，带你快速上手。

本期内容：
- 为什么 monorepo 构建慢
- Turborepo 的核心思路：依赖图 + 远程缓存
- 从零上手配置
- 实际构建速度对比

相关链接：
- Turborepo: https://turbo.build/

---

{个人推广信息}

## 章节 (Chapters)

00:00 开头
00:10 为什么 monorepo 构建慢
01:00 Turborepo 核心思路
02:30 上手配置
04:30 实际效果
05:30 总结

## 封面建议

Turborepo logo + 构建速度对比（8min → 45s），背景用深色调，突出速度提升数字。
```

**bilibili.md (excerpt)**:

```markdown
# Bilibili 发布素材

## 标题

Turborepo：让你的 monorepo 构建快 10 倍

## 标题备选

- monorepo 构建太慢？Turborepo 帮你解决
- 告别全量构建：Turborepo 实战

## 描述

{赞助商广告}

monorepo 项目构建越来越慢？Turborepo 通过依赖图分析和远程缓存，只构建真正变化的包。这期视频从原理到实操，带你快速上手。

本期内容：
- 为什么 monorepo 构建慢
- Turborepo 的核心思路：依赖图 + 远程缓存
- 从零上手配置
- 实际构建速度对比

相关链接：
- Turborepo: https://turbo.build/

## 封面建议

Turborepo logo + 构建速度对比（8min → 45s），背景用深色调，突出速度提升数字。
```

## Example 2: User provides reference material

**User**: 我想做一期关于 Cursor vs Windsurf 的对比视频，这是我的笔记 ./notes/cursor-vs-windsurf.md

**Claude**: Reads the notes file, researches both tools if needed, asks about target audience and length, then generates script, blog, youtube, and bilibili files.

## Example 3: User only provides a vague idea

**User**: 想做一期视频聊聊 AI 编程

**Claude**:

```
好的，AI 编程是个很好的话题。让我了解更多细节：

1. 你想聊哪个方面？比如：
   - AI 编程工具对比（Cursor、Copilot、Claude Code 等）
   - AI 编程的工作流和最佳实践
   - AI 对程序员的影响和未来趋势
   - 某个具体工具的深度体验
2. 面向什么观众？开发者还是泛科技人群？
3. 大概多长时间？
```
