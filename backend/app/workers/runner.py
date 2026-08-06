import asyncio
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Document, Job
from app.services.events import event_bus
from app.services.knowledge import KnowledgeEngine


class JobRunner:
    def __init__(self): self.task: asyncio.Task | None = None; self.running = False
    async def start(self): self.running = True; self.task = asyncio.create_task(self.run())
    async def stop(self):
        self.running = False
        if self.task: self.task.cancel()
    async def run(self):
        while self.running:
            async with SessionLocal() as session:
                job = await session.scalar(select(Job).where(Job.status == "queued").order_by(Job.created_at).limit(1))
                if not job: await asyncio.sleep(.5); continue
                job.status = "running"; await session.commit()
                try:
                    if job.job_type == "ingest":
                        document = await session.get(Document, job.payload["document_id"])
                        async def progress(value, stage):
                            job.progress = value; await session.commit(); await event_bus.publish(job.project_id, "document.status", {"document_id": document.id, "status": "processing" if value < 1 else "ready", "progress": value, "stage": stage})
                        await KnowledgeEngine(session).ingest(document, progress)
                    job.status = "completed"; job.progress = 1
                except Exception as exc:
                    job.status = "failed"; job.error = str(exc)
                    if job.job_type == "ingest":
                        document = await session.get(Document, job.payload["document_id"])
                        if document: document.status = "failed"
                await session.commit(); await event_bus.publish(job.project_id, "job.completed", {"job_id": job.id, "status": job.status, "error": job.error})


job_runner = JobRunner()
