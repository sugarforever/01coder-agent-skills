#!/usr/bin/env node
// srt-cues.mjs — print every SRT cue as "start_seconds | text" for scene planning.
// Usage: node srt-cues.mjs path/to/narration.srt
//        node srt-cues.mjs narration.srt --json     # machine-readable [{i,start,end,text}]
import { readFileSync } from "node:fs";

const file = process.argv[2];
const asJson = process.argv.includes("--json");
if (!file) {
  console.error("usage: node srt-cues.mjs <file.srt> [--json]");
  process.exit(1);
}

const toSec = (ts) => {
  // 00:01:23,456  ->  83.456
  const m = ts.trim().match(/(\d+):(\d+):(\d+)[,.](\d+)/);
  if (!m) return null;
  return +m[1] * 3600 + +m[2] * 60 + +m[3] + +m[4] / 1000;
};

const blocks = readFileSync(file, "utf8").replace(/\r/g, "").split(/\n\n+/);
const cues = [];
for (const b of blocks) {
  const lines = b.split("\n").filter((l) => l.trim() !== "");
  if (!lines.length) continue;
  const tl = lines.find((l) => l.includes("-->"));
  if (!tl) continue;
  const [a, z] = tl.split("-->");
  const start = toSec(a);
  const end = toSec(z);
  if (start == null) continue;
  const text = lines.slice(lines.indexOf(tl) + 1).join(" ").trim();
  cues.push({ i: cues.length + 1, start, end, text });
}

if (asJson) {
  console.log(JSON.stringify(cues, null, 2));
} else {
  for (const c of cues) {
    console.log(`${c.start.toFixed(3).padStart(9)} | ${c.text}`);
  }
  const last = cues[cues.length - 1];
  console.log(`\n${cues.length} cues · audio ends ~${last ? last.end.toFixed(1) : "?"}s`);
}
