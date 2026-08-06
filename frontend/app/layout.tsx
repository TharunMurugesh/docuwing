import "./globals.css";
import type { Metadata } from "next";
export const metadata: Metadata = { title: "Docuwing", description: "Local-first AI document workspace" };
export default function Layout({ children }: { children: React.ReactNode }) { return <html lang="en"><body>{children}</body></html> }
