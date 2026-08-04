"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "../../../../lib/api";
import { DocumentViewer, ExtractionField } from "../../../../components/document-viewer";
import { ExtractionReview } from "../../../../components/extraction-review";
import { ChatPanel } from "../../../../components/chat-panel";
export default function DocumentPage() {
  const { docId } = useParams<{docId:string}>(); const [content,setContent]=useState(""); const [fields,setFields]=useState<ExtractionField[]>([]);
  useEffect(()=>{api<{content:string}>(`/documents/${docId}/content`).then(r=>setContent(r.content)).catch(()=>{});api<{fields:ExtractionField[]}>(`/documents/${docId}`).then(r=>setFields(r.fields)).catch(()=>{});},[docId]);
  return <main className="shell"><h1>Document workspace</h1><DocumentViewer content={content} fields={fields}/><ExtractionReview documentId={docId} schemaId="current" fields={fields}/><ChatPanel documentId={docId}/></main>;
}
