"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "../../lib/api";
export default function Login() { const router = useRouter(); const [email,setEmail]=useState("demo@docuwing.local"),[password,setPassword]=useState("demo"),[error,setError]=useState(""); return <main className="center"><form className="panel stack" onSubmit={async e=>{e.preventDefault();try{const r=await api<{access_token:string}>("/auth/login",{method:"POST",body:JSON.stringify({email,password})});localStorage.setItem("token",r.access_token);router.push("/projects");}catch{setError("Unable to sign in")}}}><h1>Welcome to Docuwing</h1><input value={email} onChange={e=>setEmail(e.target.value)}/><input type="password" value={password} onChange={e=>setPassword(e.target.value)}/><button>Sign in</button>{error&&<p>{error}</p>}</form></main>; }
