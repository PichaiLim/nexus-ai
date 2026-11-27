import type { ReactNode } from "react";
import "./model-sources.css";

export const metadata = { title: "Nexus AI · Personal AI Platform" };

export default function Layout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
