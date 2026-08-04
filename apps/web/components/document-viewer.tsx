"use client";
import { useState } from "react";
export type ExtractionField = { id: string; field_name: string; value: unknown; confidence: number; validation_state: string; human_confirmed: boolean };
export function DocumentViewer({ content, fields }: { content: string; fields: ExtractionField[] }) {
  const [overlay, setOverlay] = useState(true);
  return <section className="panel"><div className="row"><h2>Document viewer</h2><button onClick={() => setOverlay(!overlay)}>{overlay ? "Hide" : "Show"} extraction overlay</button></div><pre className="document">{content}</pre>{overlay && <aside className="overlay">{fields.map(f => <div key={f.id}><strong>{f.field_name}</strong>: {String(f.value ?? "—")} <small>{f.validation_state}</small></div>)}</aside>}</section>;
}
