import { readFile } from "node:fs/promises";
import path from "node:path";

export const dynamic = "force-static";

export async function GET() {
  const html = await readFile(path.resolve(process.cwd(), "../../docs/nexus-ai-codex-handoff/nexus-ai-mockup.html"));
  return new Response(new Uint8Array(html), { headers: { "Content-Type": "text/html; charset=utf-8" } });
}
