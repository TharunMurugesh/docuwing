export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export type Project = { id:string; name:string; created_at:string };
export type Document = { id:string; filename:string; status:string; created_at:string };
export type Result = { id:string; title:string; kind:string; latest_version_id:string|null };
export type Message = { id?:string; role:"user"|"assistant"; content:string; citations?:{label:string}[] };
export async function request<T>(path:string, init?:RequestInit):Promise<T> { const response = await fetch(API+path, { ...init, headers:{ "Content-Type":"application/json", ...(init?.headers || {}) } }); if (!response.ok) throw new Error((await response.json().catch(()=>null))?.error?.message || "Request failed"); return response.json() }
