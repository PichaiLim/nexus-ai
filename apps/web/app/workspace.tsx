"use client";

import Script from "next/script";
import { memo, useEffect, useState } from "react";
import { createPortal } from "react-dom";
import ModelSources from "./model-sources";

const ShellMarkup = memo(function ShellMarkup({ markup }: { markup: string }) {
  return <div dangerouslySetInnerHTML={{ __html: markup }} />;
});

export default function Workspace({ styles, markup, script }: {
  styles: string; markup: string; script: string;
}) {
  const [mount, setMount] = useState<HTMLElement | null>(null);

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
    {mount && createPortal(<ModelSources />, mount)}
  </>;
}
