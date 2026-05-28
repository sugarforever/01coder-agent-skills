# Examples - 教程 / 配置类视频范本

这一份范本是用户认可的「教程 / 配置类视频」标准脚本 - 把 `references/script-guidelines.md` 里的 Hook 开篇结构、内嵌录制提示、节奏与判断、诚实承认约束这几条规则一次性展示出来。

**写新的教程 / 配置类脚本前，先扫一眼这份范本里 Hook 段的结构、过渡句的语气、和制作备注的两种格式（括号 vs `>` blockquote）**。

> 评论 / 拆解 / 发布解读类视频不完全适用这份范本 - 那种语境里 hook 可以是 punch line 开场（如「Karpathy 的 LLM Wiki 是什么 - 一个被严重低估的工具想法」），不必先做自我介绍。

---

## 重点看什么

阅读下面这份完整范本时，重点比对这几个段落：

1. **Hook 段** - 第一句自我介绍 → 上期承接 → 受众点名（“对于注重数据隐私的朋友来说”）→ 完整句子描述方案 → 「无论是 X、还是 Y、还是 Z，都能满足需求」整齐排比 → 软过渡（“那现在我们就开始吧”）
2. **「为什么本地也能跑」段中部** - `> 这里分享 Ollama 对 Anthropic 协议兼容的文档。` 这种内嵌 blockquote 录制提示
3. **「装 Ollama 加拉模型」段** - 「大家根据自己的硬件配置来选择模型」「在演示中，我选 qwen2.5-coder:14b」这种平视引导式，**不要**写成「这里有个关键判断」式的工程裁判腔
4. **「装 Ollama 加拉模型」段** - 24GB 跑不动 30B + 64k 的诚实换算，把硬约束摆出来
5. **「跑一次真活」段** - `（终端进入 ~/ollama-demo/，空目录）` 这种括号制作备注，与上面 blockquote 形成两种格式的对比

---

## 完整范本

下面是 `videos/20260514-claude-code-ollama/script-revised.md` 的完整内容，保留作为该类视频的引用范本。

---

```markdown
---
title: "给 Claude Code 配置基于 Ollama 的本地模型"
date: "2026-05-14"
duration: "~5-6 分钟"
platform: "YouTube / Bilibili"
---

# 给 Claude Code 配置基于 Ollama 的本地模型

> **录制说明**：
> - **Part 1（约 30s）**：Hook + 系列承接（上期 4 家云模型，本期完全本地）
> - **Part 2（约 30s）**：原理 - 还是 Anthropic 兼容端点，这次端点在 `localhost:11434`，token 字段是字面量 `"ollama"`
> - **Part 3（约 1 min）**：装 Ollama + 拉模型（pull 命令一笔带过，剪辑跳过等待）
> - **Part 4（约 45s）**：两条配置路径 - 手动 export 三行 / `ollama launch claude` 一行
> - **Part 5（约 1.5 min）**：fizzbuzz demo，真实展示本地模型 tool use
> - **Part 6（约 30s）**：64k 上下文这条硬约束
> - **Part 7（约 30s）**：本地 vs 云的边界
> - **Part 8（约 15s）**：收尾
>
> **录制前准备**：
> - `ollama pull qwen2.5-coder:14b` 已完成（约 5GB 下载，录前一晚跑完）
> - `ollama serve` 已用 `OLLAMA_CONTEXT_LENGTH=65536` 起好；如果环境变量这条路不通，改用 Modelfile 方案（脚本里给出兜底命令）
> - 空 demo 目录 `~/ollama-demo/` 备好，干净的 bun + TypeScript 环境
> - Claude Code 已装（`claude --version` 确认）
>
> **关键资料**：
> - 官方集成文档：https://docs.ollama.com/integrations/claude-code
> - Ollama 模型库：https://ollama.com/library
> - 上期视频：四家国产云模型接 Claude Code
>
> **录制机器**：MacBook Pro M3，24GB 统一内存。这是个有诚意要讲清楚的事实 - 24GB 跑不动 30B 本地模型 + 64k 上下文，所以 demo 用 14B 级。

## Hook

（终端开着，Ollama 已起）

大家好，我是小木头。在上期视频中，我们把 Claude Code 接到了 4 家国产云模型 - DeepSeek、GLM、Kimi、Qwen。今天这一期，我们给 Claude Code 配置本地模型。

对于注重数据隐私的朋友来说，本地模型是不错的选择。Ollama 让我们可以在本地环境上运行一个 Anthropic 兼容的端点，完全不依赖网络，不需要订阅，也没有账单。无论是处理敏感数据、在内网开发，还是出差时离线工作，都能满足需求。

我想，这应该是 Claude Code 用户会感兴趣的部署方案。那现在我们就开始吧。

## 为什么本地也能跑

Claude Code 启动时只看两个环境变量 - `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN`。上期我们把 URL 指到阿里云、Moonshot 那些云服务；这期，**我们把 URL 指到你笔记本上**。

> 这里分享 Ollama 对 Anthropic 协议兼容的文档。

负责在本地暴露这个 Anthropic 兼容接口的，就是 Ollama。Ollama 默认监听 `http://localhost:11434`，做了一层 Anthropic 协议适配。

有一个细节 - **`ANTHROPIC_AUTH_TOKEN` 这里填字面量 `"ollama"` 这五个字母**。不是 API key，不需要注册。它只是个占位符，绕过 Claude Code 的非空校验。

## 装 Ollama 加拉模型

Ollama 装一次就行 - macOS 直接从 [ollama.com](https://ollama.com) 下载，或者：

```bash
brew install ollama
```

装完起 daemon：

```bash
ollama serve
```

然后拉模型。大家根据自己的硬件配置来选择模型 - 我录这期用的是 24GB 内存的 M3 MacBook Pro。**24GB 跑不动 30B 级别的本地模型 + 64k 上下文**。算一下 - 30B 模型 Q4 量化 ~18GB 权重，加上 KV cache 4-8GB，加上系统占用，直接溢出。

所以，在演示中，我选 `qwen2.5-coder:14b` - 9GB 权重，开 64k 上下文也只到 14-15GB，留足余量。如果你是 32GB 以上的 Mac，可以直接 `ollama pull qwen3-coder` 上 30B 级。

（录屏开始）

```bash
ollama pull qwen2.5-coder:14b
```

<!-- 剪辑：跳过下载等待，直接到完成 -->

拉完。

## 两条配置路径

接进 Claude Code 有两条路。

**路径 A - 手动 export 三个环境变量**。跟上期 4 家云模型形式完全一致：

```bash
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_MODEL=qwen2.5-coder:14b
claude
```

> 这里分享 ollama launch claude 的文档 - https://docs.ollama.com/integrations/claude-code

**路径 B - 用 Ollama 新发的 `launch` 命令**，一行搞定：

```bash
ollama launch claude --model qwen2.5-coder:14b
```

这条命令自动设好上面那三个变量，然后直接启动 Claude Code。**强烈推荐路径 B** - 配置和启动绑在一起，不会出现“我 export 漏了哪一行”这种困扰。

## 跑一次真活

我直接进 demo 目录跑一下。

（终端进入 `~/ollama-demo/`，空目录）

```bash
cd ~/ollama-demo
ollama launch claude --model qwen2.5-coder:14b
```

（Claude Code 起来）

给它一个真任务 - 不是“你好介绍一下你自己”那种摆设。本地小模型能不能做 agentic 编码，要看 tool use 稳不稳。

我让它写一个 fizzbuzz：

> 帮我写一个 `fizzbuzz.ts`，1 到 30，能被 3 整除打 fizz、5 打 buzz、15 打 fizzbuzz，写完用 `bun run fizzbuzz.ts` 跑一下验证输出。

（Claude Code 开始干活）

<!-- TODO: 录制时记录真实输出。期待行为：调用 Write 写文件 → 调用 Bash 跑 bun → 看到 30 行输出 → 总结。失败的话也照实展示，可能在 tool 调用格式上出错，或者输出多/少一行。 -->

这个任务考点很清楚 - **Write tool 写文件 + Bash tool 跑命令 + 一段薄逻辑**。14B 本地模型能扛下来，说明它在 Claude Code 这个 harness 下能做日常 coding。

## 64k 上下文这条硬约束

讲一个**录制前差点翻车的坑**。

Ollama 默认 context length 是 2048 或 4096，**Claude Code 第一句对话就会爆**。系统提示词加 tool schema 加用户问题，光这些就远超过这个长度。

官方文档明确写了 - **至少 64k**。两种设置方法。

**方法一 - 环境变量起 daemon**：

```bash
OLLAMA_CONTEXT_LENGTH=65536 ollama serve
```

**方法二 - 写一个自定义 Modelfile**：

```bash
cat > Modelfile <<EOF
FROM qwen2.5-coder:14b
PARAMETER num_ctx 65536
EOF
ollama create qwen2.5-coder:14b-64k -f Modelfile
```

然后用 `qwen2.5-coder:14b-64k` 这个 tag 启动。我用的是方法一，简单。

## 本地 vs 云，什么时候选哪个

最后讲一下边界 - 本地不是云的替代品，是补充。

**走本地的场景**：

- **隐私敏感** - 客户代码、医疗数据、未发布产品，根本不想出网
- **内网开发** - 外网访问受限，云端 API 进不来
- **出差离线** - 飞机上、酒店烂网，本地完全不依赖网络

**走云的场景**：

- 日常 coding，要 Sonnet、Opus、Kimi K2.6、Qwen3-Coder Plus 这种顶配能力
- 大项目长上下文，本地 14B 扛不动

诚实讲 - **14B 本地模型的能力上限明显低于云端旗舰**。但在该用本地的场景里，它够用，而且永远在你手上。

## 收尾

回顾一下 - **Ollama 跑在 `localhost:11434`，token 写字面量 `"ollama"`，一条 `ollama launch claude --model X` 启动**。注意把 daemon 的 context length 调到 64k 以上，不然第一句话就爆。

官方文档和上期 4 家国产云模型的视频链接我放在描述里。今天的分享就到这里，感谢大家收看，我们下期再见。
```
