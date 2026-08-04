export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-slate-950 text-slate-100">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold tracking-tight text-cyan-400 mb-4">
          Docuwing Platform
        </h1>
      </div>
      <p className="text-slate-400 text-lg max-w-2xl text-center">
        Engine-driven document intelligence, structured extraction, layout analysis, and hybrid RAG.
      </p>
      <div className="mt-8 flex gap-4">
        <span className="px-3 py-1 bg-cyan-950 border border-cyan-800 text-cyan-300 rounded-full text-sm font-semibold">
          Phase 0 Baseline Complete
        </span>
      </div>
    </main>
  );
}
