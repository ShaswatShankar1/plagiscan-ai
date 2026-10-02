import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ShieldCheck, FileSearch, RefreshCw, CheckCircle } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50">
      <header className="px-6 py-4 border-b bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
          <h1 className="text-xl font-bold">PlagiScan AI</h1>
        </div>
        <nav className="flex items-center gap-4">
          <Link href="/analyze" className="text-sm font-medium hover:text-indigo-600 transition-colors">Analyzer</Link>
          <Link href="/dashboard" className="text-sm font-medium hover:text-indigo-600 transition-colors">Dashboard</Link>
        </nav>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-24 flex flex-col items-center text-center">
        <h2 className="text-5xl font-extrabold tracking-tight mb-6 max-w-3xl">
          Detect Plagiarism. <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Improve Originality.</span>
        </h2>
        <p className="text-xl text-slate-600 dark:text-slate-400 mb-10 max-w-2xl">
          Analyze documents for textual similarity, understand exactly what was matched, rewrite problematic passages, and verify the result.
        </p>
        
        <div className="flex gap-4 mb-20">
          <Link href="/analyze">
            <Button size="lg" className="bg-indigo-600 hover:bg-indigo-700 text-white gap-2">
              <FileSearch className="w-5 h-5" />
              Start Checking
            </Button>
          </Link>
          <Link href="/analyze?sample=true">
            <Button size="lg" variant="outline" className="gap-2">
              Try Sample Text
            </Button>
          </Link>
        </div>

        <div className="grid md:grid-cols-3 gap-8 w-full text-left">
          <FeatureCard 
            icon={<FileSearch className="w-6 h-6 text-blue-500" />}
            title="Multi-Layer Detection"
            description="Uses exact phrase matching, fuzzy matching, and semantic similarity via AI embeddings to find hidden matches."
          />
          <FeatureCard 
            icon={<RefreshCw className="w-6 h-6 text-purple-500" />}
            title="AI Paraphrasing"
            description="Intelligently rewrite flagged passages to improve originality while preserving meaning and academic integrity."
          />
          <FeatureCard 
            icon={<CheckCircle className="w-6 h-6 text-emerald-500" />}
            title="Verify & Export"
            description="Iteratively re-check your document and download a comprehensive originality report for peace of mind."
          />
        </div>
      </main>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow">
      <div className="w-12 h-12 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{description}</p>
    </div>
  );
}
