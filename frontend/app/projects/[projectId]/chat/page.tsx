"use client";
import { useEffect, useState } from "react";
import Workspace from "../../../../components/Workspace";
import { Project, request } from "../../../../lib/api";
export default function ProjectChat({ params }: { params: Promise<{projectId:string}> }) { const [project,setProject]=useState<Project|null>(null); useEffect(()=>{params.then(({projectId})=>request<Project>(`/api/projects/${projectId}`).then(setProject))},[params]); return project?<Workspace project={project}/>:<p className="empty">Loading workspace…</p> }
