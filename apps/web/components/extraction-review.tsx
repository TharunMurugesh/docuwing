"use client";
import { ExtractionField } from "./document-viewer";
import { api } from "../lib/api";
export function ExtractionReview({ documentId, schemaId, fields }: { documentId: string; schemaId: string; fields: ExtractionField[] }) {
  async function confirm(field: ExtractionField) { await api(`/documents/${documentId}/extraction/${schemaId}/fields/${field.id}`, { method: "PATCH", body: JSON.stringify({ confirmed: true }) }); location.reload(); }
  return <section className="panel"><h2>Extraction review</h2>{fields.map(field => <div className="row" key={field.id}><span><strong>{field.field_name}</strong>: {String(field.value ?? "Not extracted")}</span><button onClick={() => confirm(field)}>Confirm</button></div>)}</section>;
}
