// capture: pictures of fixed views of a web UI, with the layout faults and accessibility problems found in each.
// Owned by the scaffold's web-ui module (docs/process/modules/web-ui.md, "Review"). Framework-independent: it only
// needs a URL. Node 20+ with the devDependency playwright-core (and axe-core for --axe); it drives the installed
// Edge or Chrome, so no browser is downloaded.
//
//   node docs/process/tools/web/capture.mjs <views.json> [--out <folder>] [--base-url <url>] [--axe]
//        [--browser msedge|chrome|chromium] [--only <key>,...]
//
// views.json:
//   {
//     "baseUrl": "http://localhost:5173",          (or --base-url; a view's path is joined to it)
//     "boxes": "[data-box]",                        (optional: elements that must not overlap)
//     "views": [
//       { "key": "settings@390", "path": "/settings", "width": 390, "height": 844,
//         "colorScheme": "dark", "fullPage": false,
//         "actions": [ { "click": "text=Advanced" }, { "fill": ["#name", "Ada"] }, { "press": "Escape" },
//                      { "wait": 300 }, { "waitFor": ".loaded" } ] }
//     ]
//   }
//
// Writes <out>/<key>.png (fixed viewport unless fullPage) and <out>/report.json; prints one line per view.
// Faults: horizontal page scroll, text cut short, overlapping boxes, interactive targets under 24x24 px.
// Exit code: 0 no faults, 1 faults found, 2 a wrong command line or view list, 3 a view could not be taken.
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join, resolve } from "node:path";
import { parseArgs } from "node:util";

const usage =
  "node capture.mjs <views.json> [--out <folder>] [--base-url <url>] [--axe] [--browser msedge|chrome|chromium] [--only <keys>]";
const { values: o, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    out: { type: "string" },
    "base-url": { type: "string" },
    axe: { type: "boolean" },
    browser: { type: "string" },
    only: { type: "string" },
    help: { type: "boolean", short: "h" },
  },
});
const fail = (msg, code = 2) => {
  console.error(`capture: ${msg}\n${usage}`);
  process.exit(code);
};
if (o.help) {
  console.log(usage);
  process.exit(0);
}
if (positionals.length !== 1) fail("one views file");

let list;
try {
  list = JSON.parse(readFileSync(positionals[0], "utf8"));
} catch (e) {
  fail(`cannot read ${positionals[0]}: ${e.message}`);
}
const baseUrl = o["base-url"] ?? list.baseUrl;
const only = o.only ? new Set(o.only.split(",")) : undefined;
const views = (list.views ?? []).filter((v) => !only || only.has(v.key));
if (!views.length) fail("no views (or none matching --only)");
for (const v of views) {
  if (!v.key || !/^[\w.@-]+$/.test(v.key)) fail(`view key "${v.key}": letters, digits, . @ - _ only (it is a file name)`);
  if (!(v.width > 0)) fail(`view ${v.key}: a width in pixels`);
}
const out = resolve(o.out ?? join("tmp", "capture"));
mkdirSync(out, { recursive: true });

const require = createRequire(join(process.cwd(), "package.json"));
const { chromium } = require("playwright-core");
const axeSource = o.axe ? readFileSync(require.resolve("axe-core/axe.min.js"), "utf8") : undefined;

async function launch() {
  const channels = o.browser ? [o.browser] : ["msedge", "chrome", "chromium"];
  for (const channel of channels) {
    try {
      return await chromium.launch({ channel: channel === "chromium" ? undefined : channel, headless: true });
    } catch {
      // try the next one
    }
  }
  fail(`no browser could be started (tried ${channels.join(", ")})`, 3);
}

// The page's side: measures only, judging is in the report lines below.
function findFaults(boxesSelector) {
  const name = (el) => {
    const id = el.id ? `#${el.id}` : "";
    const cls = typeof el.className === "string" && el.className.trim() ? `.${el.className.trim().split(/\s+/).slice(0, 2).join(".")}` : "";
    const text = (el.textContent ?? "").trim().slice(0, 30);
    return `${el.tagName.toLowerCase()}${id}${cls}${text ? ` "${text}"` : ""}`;
  };
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.visibility !== "hidden" && s.display !== "none" && r.width > 0 && r.height > 0;
  };
  const faults = [];
  const doc = document.documentElement;
  if (doc.scrollWidth > window.innerWidth + 1) {
    faults.push({ kind: "horizontal-scroll", what: `page is ${doc.scrollWidth}px wide in a ${window.innerWidth}px viewport` });
  }
  // Text cut short: content wider than its box (or taller where overflow is hidden), innermost only. Whole-pixel
  // scroll sizes miss fractions, so the element's own text is also measured with a Range against its content box.
  const cut = [];
  for (const el of document.querySelectorAll("body *")) {
    if (el.closest("svg, [data-scroll], input, textarea, select") || !visible(el)) continue;
    const s = getComputedStyle(el);
    if (["auto", "scroll"].includes(s.overflowX) || ["auto", "scroll"].includes(s.overflowY)) continue;
    let wide = el.scrollWidth > el.clientWidth + 0.5 && el.clientWidth > 0;
    const tall = s.overflowY === "hidden" && el.scrollHeight > el.clientHeight + 0.5 && el.clientHeight > 0;
    if (!wide && s.overflowX === "hidden") {
      const range = document.createRange();
      for (const node of el.childNodes) {
        if (node.nodeType !== Node.TEXT_NODE || !node.textContent.trim()) continue;
        range.selectNodeContents(node);
        const text = range.getBoundingClientRect();
        const box = el.getBoundingClientRect();
        const right = box.right - parseFloat(s.paddingRight) - parseFloat(s.borderRightWidth);
        if (text.right > right + 0.5) wide = true;
      }
    }
    if (wide || tall) cut.push(el);
  }
  for (const el of cut) {
    if (!cut.some((other) => other !== el && el.contains(other))) {
      faults.push({ kind: "text-cut", what: name(el) });
    }
  }
  if (boxesSelector) {
    const boxes = [...document.querySelectorAll(boxesSelector)].filter(visible);
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i].getBoundingClientRect();
        const b = boxes[j].getBoundingClientRect();
        if (boxes[i].contains(boxes[j]) || boxes[j].contains(boxes[i])) continue;
        if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1) {
          faults.push({ kind: "overlap", what: `${name(boxes[i])} and ${name(boxes[j])}` });
        }
      }
    }
  }
  // Target size (WCAG 2.5.8, AA): interactive elements at least 24x24 px; links inside running text are exempt.
  const interactive = "button, a[href], input:not([type=hidden]), select, textarea, [role=button], [role=link], [role=tab], [role=checkbox], [tabindex]:not([tabindex='-1'])";
  for (const el of document.querySelectorAll(interactive)) {
    if (!visible(el)) continue;
    if (el.tagName === "A" && getComputedStyle(el).display === "inline") continue;
    const r = el.getBoundingClientRect();
    if (r.width < 24 || r.height < 24) faults.push({ kind: "small-target", what: `${name(el)} ${Math.round(r.width)}x${Math.round(r.height)}px` });
  }
  return faults;
}

async function act(page, action) {
  if (action.click) await page.click(action.click);
  else if (action.fill) await page.fill(action.fill[0], action.fill[1]);
  else if (action.press) await page.keyboard.press(action.press);
  else if (action.waitFor) await page.waitForSelector(action.waitFor);
  else if (action.wait) await page.waitForTimeout(action.wait);
  else throw new Error(`unknown action ${JSON.stringify(action)}`);
}

const browser = await launch();
const report = [];
let faultCount = 0;
let failed = 0;
for (const view of views) {
  const height = view.height ?? (view.width < 1024 ? 844 : 900);
  const context = await browser.newContext({
    viewport: { width: view.width, height },
    deviceScaleFactor: view.scale ?? 1,
    colorScheme: view.colorScheme ?? "light",
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  const entry = { key: view.key, url: "", width: view.width, height, faults: [], axe: undefined, error: undefined };
  try {
    entry.url = baseUrl && !/^[a-z]+:/i.test(view.path ?? "") ? new URL(view.path ?? "/", baseUrl).href : view.path;
    if (!entry.url) throw new Error("no URL: give baseUrl or a full path");
    await page.goto(entry.url, { waitUntil: "networkidle" });
    for (const action of view.actions ?? []) await act(page, action);
    await page.screenshot({ path: join(out, `${view.key}.png`), fullPage: Boolean(view.fullPage) });
    entry.faults = await page.evaluate(findFaults, list.boxes ?? "");
    if (axeSource) {
      await page.addScriptTag({ content: axeSource });
      const result = await page.evaluate(() =>
        window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } }),
      );
      entry.axe = result.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help }));
    }
  } catch (e) {
    entry.error = e.message.split("\n")[0];
    failed++;
  }
  await context.close();
  const problems = entry.faults.length + (entry.axe?.length ?? 0);
  faultCount += problems;
  report.push(entry);
  if (entry.error) console.log(`${view.key}: not taken: ${entry.error}`);
  else if (!problems) console.log(`${view.key}: ok`);
  else {
    const kinds = {};
    for (const f of entry.faults) kinds[f.kind] = (kinds[f.kind] ?? 0) + 1;
    for (const a of entry.axe ?? []) kinds[`a11y:${a.id}`] = a.nodes;
    console.log(`${view.key}: ${Object.entries(kinds).map(([k, n]) => `${k} ${n}`).join(", ")}`);
  }
}
await browser.close();
writeFileSync(join(out, "report.json"), JSON.stringify(report, null, 2) + "\n");
console.log(`capture: ${views.length} views to ${out}; ${faultCount} problems, ${failed} not taken (details: report.json)`);
process.exit(failed ? 3 : faultCount ? 1 : 0);
