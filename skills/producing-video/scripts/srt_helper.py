#!/usr/bin/env python3
"""SRT 帮手：build（transcription verbose_json → SRT）+ correct（文本级 LLM 校正）。

correct 只改字幕文本、按原条目重挂时间戳/编号 —— 时间轴与条数零风险（subtitle-correction
的铁律：NEVER modify timestamps / numbering / count）。LLM 出错或长度不符则原样退回。
仅用标准库（urllib），无第三方依赖。
"""
import sys, json, re, argparse, urllib.request


def ts(sec):
    if sec is None or sec < 0:
        sec = 0
    ms = int(round(float(sec) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build(a):
    data = json.load(open(a.input, encoding="utf-8"))
    segs = data.get("segments") or []
    out = []
    for i, seg in enumerate(segs, 1):
        out.append(f"{i}\n{ts(seg.get('start'))} --> {ts(seg.get('end'))}\n{(seg.get('text') or '').strip()}\n")
    open(a.output, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"built {len(segs)} cues -> {a.output}")


def parse_srt(path):
    blocks = re.split(r"\n\s*\n", open(path, encoding="utf-8").read().strip())
    cues = []
    for b in blocks:
        lines = b.splitlines()
        if len(lines) >= 3:
            cues.append({"num": lines[0], "time": lines[1], "text": "\n".join(lines[2:]).strip()})
    return cues


def chat(base, key, model, system, user):
    body = json.dumps({"model": model, "temperature": 0,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def correct(a):
    cues = parse_srt(a.input)
    if not cues:
        print("no cues, copy through", file=sys.stderr)
        open(a.output, "w", encoding="utf-8").write(open(a.input, encoding="utf-8").read())
        return
    sysmsg = (
        "你是中文字幕校对器。输入是一个 JSON 数组，每个元素是一条字幕文本（语音识别结果，"
        "可能有同音字、英文专名/术语拼写错误、中英文间空格与标点不规整）。逐条修正这些错误，"
        "规整标点与中英文空格。严格要求：(1) 返回同样长度、同样顺序的 JSON 字符串数组；"
        "(2) 不合并、不拆分、不增删任何条目；(3) 只改文本，不要任何解释或多余字段。"
        + (f" 已知术语（按此拼写为准）：{a.terms}" if a.terms else ""))
    user = json.dumps([c["text"] for c in cues], ensure_ascii=False)
    fixed = None
    try:
        resp = chat(a.base, a.key, a.model, sysmsg, user)
        m = re.search(r"\[.*\]", resp, re.S)
        fixed = json.loads(m.group(0)) if m else None
    except Exception as e:
        print(f"correction skipped (LLM error: {e})", file=sys.stderr)
    if not isinstance(fixed, list) or len(fixed) != len(cues):
        got = None if fixed is None else len(fixed)
        print(f"correction skipped (len {got} != {len(cues)}); keeping raw", file=sys.stderr)
        open(a.output, "w", encoding="utf-8").write(open(a.input, encoding="utf-8").read())
        return
    out = [f"{c['num']}\n{c['time']}\n{str(t).strip()}\n" for c, t in zip(cues, fixed)]
    open(a.output, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"corrected {len(cues)} cues -> {a.output}")


p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)
b = sub.add_parser("build"); b.add_argument("input"); b.add_argument("output"); b.set_defaults(fn=build)
c = sub.add_parser("correct")
c.add_argument("input"); c.add_argument("output")
c.add_argument("--base", required=True); c.add_argument("--key", required=True)
c.add_argument("--model", required=True); c.add_argument("--terms", default="")
c.set_defaults(fn=correct)
a = p.parse_args()
a.fn(a)
