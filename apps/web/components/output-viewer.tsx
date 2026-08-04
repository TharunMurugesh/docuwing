"use client";
export function OutputViewer({ format, content }: { format: string; content: string }) { return <section className="panel"><h2>{format.replaceAll("_", " ")}</h2><pre className="document">{content}</pre></section>; }
