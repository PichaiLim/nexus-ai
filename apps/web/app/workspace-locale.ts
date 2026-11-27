import { catalog, localeOptions } from "./locale";

const options = localeOptions.map(({ id, label }) => `<option value="${id}" lang="${id}">${label}</option>`).join("");
export const languageControl = `<select id="nexus-language" aria-label="Language" onchange="nexusChangeLanguage(this.value)">${options}</select>`;

export const languageRuntime = `const nexusCatalog=${JSON.stringify(catalog)};
` + String.raw`
let nexusLocale = "en";
try {
  const saved = localStorage.getItem("nexus-language");
  if (Object.hasOwn(nexusCatalog, saved)) nexusLocale = saved;
} catch {}
document.documentElement.lang = nexusLocale;
window.dispatchEvent(new CustomEvent("nexus-language-change", { detail: nexusLocale }));

function nexusText(message) {
  if (nexusLocale === "en") return message;
  const messages = nexusCatalog[nexusLocale];
  if (Object.hasOwn(messages, message)) return messages[message];
  const overviewCount = message.match(/^(\d+) (loaded in memory|tasks running|connected)$/);
  if (overviewCount) {
    return nexusText("{count} " + overviewCount[2]).replace("{count}", overviewCount[1]);
  }
  if (/^(Hybrid|Local|Offline|Cloud) mode$/.test(message)) {
    return nexusText("{mode} mode").replace("{mode}", nexusText(message.slice(0, -5)));
  }
  if (message.startsWith("· ")) return "· " + nexusText(message.slice(2));
  const breadcrumb = message.match(/^(.*?)\s+\/$/);
  if (breadcrumb) return nexusText(breadcrumb[1]) + " /";
  return message;
}

function nexusTranslate(root) {
  if (nexusLocale === "en" || !root) return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    if (node.parentElement?.closest(".listline b, option[lang]")) continue;
    const label = node.textContent.trim();
    if (label) node.textContent = node.textContent.replace(label, nexusText(label));
  }
  for (const element of root.querySelectorAll("[aria-label], [placeholder]")) {
    for (const attribute of ["aria-label", "placeholder"]) {
      const label = element.getAttribute(attribute);
      if (label) element.setAttribute(attribute, nexusText(label));
    }
  }
}

function nexusChangeLanguage(value) {
  nexusLocale = Object.hasOwn(nexusCatalog, value) ? value : "en";
  document.documentElement.lang = nexusLocale;
  try { localStorage.setItem("nexus-language", nexusLocale); } catch {}
  render();
  document.getElementById("nexus-language")?.focus();
  window.dispatchEvent(new CustomEvent("nexus-language-change", { detail: nexusLocale }));
}
`;
