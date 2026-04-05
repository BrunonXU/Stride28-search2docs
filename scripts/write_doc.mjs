#!/usr/bin/env node
/**
 * write_doc.mjs — 将 MDX 文件写入腾讯文档
 *
 * 纯 CLI 封装，不依赖 mcporter SDK。通过临时 JSON 文件传参给 mcporter CLI，
 * 绕过命令行长度限制。
 *
 * 用法：
 *   node scripts/write_doc.mjs search --keyword "关键词"
 *   node scripts/write_doc.mjs create --title "文档标题" --mdx-file output.mdx
 *   node scripts/write_doc.mjs append --file-id FILE_ID --mdx-file output.mdx
 */

import { readFileSync, writeFileSync, unlinkSync } from "fs";
import { execSync } from "child_process";
import { tmpdir } from "os";
import { join } from "path";

const args = process.argv.slice(2);
const command = args[0];

function getArg(name) {
  const idx = args.indexOf(name);
  return idx !== -1 && idx + 1 < args.length ? args[idx + 1] : null;
}

/**
 * 调用 mcporter CLI，大参数通过临时 JSON 文件传递。
 */
function callMcporter(tool, argsObj) {
  const tmpFile = join(tmpdir(), `mcporter_args_${Date.now()}.json`);
  writeFileSync(tmpFile, JSON.stringify(argsObj), "utf-8");

  try {
    // 尝试 --args-file（mcporter 0.8+ 支持）
    const result = execSync(
      `mcporter call tencent-docs ${tool} --args-file "${tmpFile}"`,
      { encoding: "utf-8", timeout: 60000 }
    );
    return result.trim();
  } catch (e1) {
    // --args-file 不支持，尝试直接传 --args（可能因为太长失败）
    try {
      const jsonStr = JSON.stringify(argsObj);
      if (jsonStr.length > 8000) {
        throw new Error("JSON 太长，无法通过命令行传递");
      }
      const escaped = jsonStr.replace(/"/g, '\\"');
      const result = execSync(
        `mcporter call tencent-docs ${tool} --args "${escaped}"`,
        { encoding: "utf-8", timeout: 60000 }
      );
      return result.trim();
    } catch (e2) {
      console.error("mcporter CLI 调用失败。");
      console.error("临时 JSON 文件保留在:", tmpFile);
      console.error("你可以手动执行:");
      console.error(`  mcporter call tencent-docs ${tool} --args '${JSON.stringify(argsObj).slice(0, 200)}...'`);
      throw e1;
    }
  } finally {
    try { unlinkSync(tmpFile); } catch {}
  }
}

// 先检查 mcporter 是否可用
try {
  execSync("mcporter --version", { encoding: "utf-8", stdio: "pipe" });
} catch {
  console.error("错误：mcporter 未安装。请先运行 npm install -g mcporter");
  process.exit(1);
}

// 检查 tencent-docs 是否配置
try {
  const list = execSync("mcporter list 2>&1", { encoding: "utf-8" });
  if (!list.includes("tencent-docs")) {
    console.error("错误：tencent-docs 未配置。");
    console.error("请访问 https://docs.qq.com/scenario/open-claw.html 获取 Token，然后执行：");
    console.error('  mcporter config add tencent-docs "https://docs.qq.com/openapi/mcp" --header "Authorization=$TOKEN" --transport http --scope home');
    process.exit(1);
  }
} catch {
  console.error("错误：无法执行 mcporter list");
  process.exit(1);
}

try {
  switch (command) {
    case "search": {
      const keyword = getArg("--keyword");
      if (!keyword) { console.error("缺少 --keyword"); process.exit(1); }
      const result = execSync(
        `mcporter call tencent-docs manage.search_file search_key:"${keyword}"`,
        { encoding: "utf-8", timeout: 30000 }
      );
      console.log(result.trim());
      break;
    }

    case "create": {
      const title = getArg("--title");
      const mdxFile = getArg("--mdx-file");
      if (!title || !mdxFile) { console.error("缺少 --title 或 --mdx-file"); process.exit(1); }
      const mdx = readFileSync(mdxFile, "utf-8");
      console.log(`正在创建文档「${title}」(${mdx.length} 字符)...`);
      console.log(callMcporter("create_smartcanvas_by_mdx", { title, mdx }));
      break;
    }

    case "append": {
      const fileId = getArg("--file-id");
      const mdxFile = getArg("--mdx-file");
      if (!fileId || !mdxFile) { console.error("缺少 --file-id 或 --mdx-file"); process.exit(1); }
      const content = readFileSync(mdxFile, "utf-8");
      console.log(`正在追加到文档 ${fileId} (${content.length} 字符)...`);
      console.log(callMcporter("smartcanvas.edit", {
        file_id: fileId, action: "INSERT_AFTER", content
      }));
      break;
    }

    default:
      console.error("用法：");
      console.error("  node write_doc.mjs search --keyword '关键词'");
      console.error("  node write_doc.mjs create --title '标题' --mdx-file output.mdx");
      console.error("  node write_doc.mjs append --file-id FILE_ID --mdx-file output.mdx");
      process.exit(1);
  }
} catch (e) {
  console.error("错误:", e.message);
  process.exit(1);
}
