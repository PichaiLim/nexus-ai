import { readFile } from "node:fs/promises";
import path from "node:path";
import Workspace from "./workspace";
import { languageControl, languageRuntime } from "./workspace-locale";

export default async function Page() {
  const reference = await readFile(path.resolve(process.cwd(), "../../docs/nexus-ai-codex-handoff/nexus-ai-mockup.html"), "utf8");
  const styles = reference.match(/<style>([\s\S]*?)<\/style>/)?.[1];
  const parts = reference.match(/<body>([\s\S]*?)<script>([\s\S]*?)<\/script><\/body>/);
  if (!styles || !parts) throw new Error("The Nexus workspace reference is missing its styles or runtime");

  const [, markup, originalScript] = parts;
  const nav = "['MODEL STUDIO',[";
  const render = "function renderContent(){const map={";
  if (!originalScript.includes(nav) || !originalScript.includes(render)) {
    throw new Error("The Nexus workspace reference changed its navigation hooks");
  }

  const script = languageRuntime + originalScript
    .replace(nav, `${nav}['Model Sources','server'],`)
    .replace('<div class="avatar" title="Demo administrator">', `${languageControl}<div class="avatar" title="Demo administrator">`)
    .replace(render, `function renderContent(){
      const languageControl = $('nexus-language');
      if (languageControl) languageControl.value = nexusLocale;
      nexusTranslate($('sidebar'));
      nexusTranslate($('top'));
      if(S.page==='Model Sources' && $('model-sources-root')) return;
      const map={'Model Sources':()=>'<div id="model-sources-root"></div>',`)
    .replace("$('content').innerHTML=(map[S.page]||overview)()", `$('content').innerHTML=(map[S.page]||overview)();
      const content = $('content');
      if(S.page==='Overview') nexusTranslate(content);
      else for(const label of content.querySelectorAll('.pagehead h1, .pagehead .eyebrow')) nexusTranslate(label)`)
    .replace("a[0].toLowerCase().includes(q.toLowerCase())", "[a[0],nexusText(a[0])].some(label=>label.toLowerCase().includes(q.trim().toLowerCase()))")
    .replace("null);searchPages('')", "null);nexusTranslate($('overlay'));searchPages('')")
    .replace("No pages found</div>'}", "No pages found</div>';nexusTranslate($('searchresults'))}")
    .replaceAll("Local-first · Demo", "Local-first workspace")
    .replace("Nexus AI / v0.1 prototype", "Nexus AI / v0.1")
    .replace("localStorage.getItem('nexus-ai-demo-v1')",
      "(localStorage.getItem('nexus-ai-workspace-v1')||localStorage.getItem('nexus-ai-demo-v1'))")
    .replace("localStorage.setItem('nexus-ai-demo-v1'", "localStorage.setItem('nexus-ai-workspace-v1'");

  return <Workspace styles={styles} markup={markup} script={script} />;
}
