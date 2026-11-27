"use client";

import Script from "next/script";
import { memo, useEffect, useState } from "react";
import { createPortal } from "react-dom";
import ModelSources from "./model-sources";
import { resolveLocale, type Locale } from "./locale";

const ShellMarkup = memo(function ShellMarkup({ markup }: { markup: string }) {
  return <div dangerouslySetInnerHTML={{ __html: markup }} />;
});

export default function Workspace({ styles, markup, script }: {
  styles: string; markup: string; script: string;
}) {
  const [mount, setMount] = useState<HTMLElement | null>(null);
  const [locale, setLocale] = useState<Locale>("en");

  useEffect(() => {
    const updateLocale = () => setLocale(resolveLocale(document.documentElement.lang));
    updateLocale();
    window.addEventListener("nexus-language-change", updateLocale);
    return () => window.removeEventListener("nexus-language-change", updateLocale);
  }, []);

  useEffect(() => {
    const content = document.getElementById("content");
    if (!content) return;
    const updateMount = () => setMount(document.getElementById("model-sources-root"));
    const observer = new MutationObserver(updateMount);
    observer.observe(content, { childList: true });
    updateMount();
    return () => observer.disconnect();
  }, []);

  return <>
    <style>{styles}</style>
    <ShellMarkup markup={markup} />
    <Script id="nexus-workspace" strategy="afterInteractive">{script}</Script>
    {mount && createPortal(<ModelSources locale={locale} />, mount)}
  </>;
}
