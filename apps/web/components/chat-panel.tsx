"use client";
import { useState } from "react";
import { api } from "../lib/api";
export function ChatPanel({ documentId }: { documentId: string }) { const [question, setQuestion] = useState(""); const [answer, setAnswer] = useState(""); return <section className="panel stack"><h2>Grounded chat</h2><input value={question} onChange={e => setQuestion(e.target.value)} placeholder="Ask about this document"/><button onClick={async () => setAnswer((await api<{answer:string}>(`/documents/${documentId}/chat`, {method:"POST", body:JSON.stringify({question})})).answer)}>Ask</button>{answer && <p>{answer}</p>}</section>; }
