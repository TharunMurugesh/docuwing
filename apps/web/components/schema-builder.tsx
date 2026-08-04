"use client";
import { useState } from "react";
import { api } from "../lib/api";
export function SchemaBuilder({ projectId }: { projectId: string }) {
  const [name, setName] = useState("Invoice"); const [field, setField] = useState("total"); const [message, setMessage] = useState("");
  async function submit(e: React.FormEvent) { e.preventDefault(); await api("/schemas", { method: "POST", body: JSON.stringify({ project_id: projectId, name, fields: [{ name: field, field_type: "string", required: false, projection_hint: "fact" }] }) }); setMessage("Schema created."); }
  return <form className="panel stack" onSubmit={submit}><h2>Schema builder</h2><input value={name} onChange={e => setName(e.target.value)} placeholder="Schema name"/><input value={field} onChange={e => setField(e.target.value)} placeholder="Field name"/><p className="muted">New fields default to the <code>fact</code> projection hint.</p><button>Create schema</button>{message && <p>{message}</p>}</form>;
}
