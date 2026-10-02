"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, UploadCloud, Play, Download, Wand2, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import axios from 'axios';

export default function AnalyzePage() {
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<null | any>(null);
  const [error, setError] = useState<string | null>(null);

  const [isRewriting, setIsRewriting] = useState(false);
  const [rewriteError, setRewriteError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setIsAnalyzing(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/analyze', { text });
      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Failed to analyze document");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRewrite = async (matchId: string, segment: string) => {
    setIsRewriting(true);
    setRewriteError(null);
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/rewrite', { text: segment, mode: "Standard" });
      const newText = text.replace(segment, response.data.rewritten);
      setText(newText);
      alert("Text rewritten! Analysis should be re-run manually.");
    } catch (err: any) {
      setRewriteError(err.response?.data?.detail || err.message || "Failed to rewrite text");
    } finally {
      setIsRewriting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950">
      <header className="px-6 py-4 border-b bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 flex items-center justify-between sticky top-0 z-10 w-full">
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="ghost" size="icon"><ArrowLeft className="w-5 h-5" /></Button>
          </Link>
          <h1 className="text-lg font-semibold">Document Analysis</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="gap-2">
            <UploadCloud className="w-4 h-4" /> Upload
          </Button>
          <Button size="sm" className="gap-2 bg-indigo-600 hover:bg-indigo-700 text-white" onClick={handleAnalyze} disabled={isAnalyzing}>
            {isAnalyzing ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Play className="w-4 h-4" />}
            {isAnalyzing ? "Analyzing..." : "Analyze Document"}
          </Button>
        </div>
      </header>

      <main className="flex-1 p-6 flex flex-col lg:flex-row gap-6 overflow-hidden">
        {/* Editor Area */}
        <div className="w-full lg:w-2/3 flex flex-col gap-4">
          <Card className="flex-1 flex flex-col border-slate-200 dark:border-slate-800 p-0 overflow-hidden">
            <div className="p-2 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 font-medium px-4 bg-slate-50 dark:bg-slate-900">
              <span>Text Editor</span>
              <span>{text.split(/\s+/).filter(w => w.length > 0).length} Words | {text.length} Characters</span>
            </div>
            <div className="flex-1 flex flex-col p-4 relative">
              <Textarea
                placeholder="Paste your text here or upload a document to begin analysis... Try pasting a sentence from Wikipedia about Artificial Intelligence!"
                className="flex-1 resize-none border-0 focus-visible:ring-0 text-base leading-relaxed bg-transparent w-full h-full min-h-[400px]"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </div>
          </Card>
        </div>

        {/* Results Area */}
        <div className="w-full lg:w-1/3 flex flex-col gap-4 overflow-y-auto pr-2">
          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-sm flex gap-3 items-start">
              <AlertTriangle className="w-5 h-5 shrink-0" />
              <p>{error}</p>
            </div>
          )}

          {rewriteError && (
             <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-sm flex gap-3 items-start">
             <AlertTriangle className="w-5 h-5 shrink-0" />
             <p>{rewriteError}</p>
           </div>
          )}

          {!results && !error ? (
            <Card className="flex-1 border-dashed bg-transparent border-slate-300 dark:border-slate-700 flex flex-col items-center justify-center text-center p-8 mt-4">
              <UploadCloud className="w-12 h-12 text-slate-400 mb-4" />
              <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-2">No Analysis Yet</h3>
              <p className="text-sm text-slate-500">Paste text or upload a document and click Analyze to see similarity results.</p>
            </Card>
          ) : results ? (
            <div className="space-y-4">
              <Card className="border-slate-200 dark:border-slate-800">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Similarity Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-end justify-between mb-2">
                    <span className="text-4xl font-bold text-red-500">{results.similarity}%</span>
                    <span className={`text-sm font-medium py-1 px-2 rounded-md ${
                      results.risk === 'High' ? 'bg-red-100 text-red-700' :
                      results.risk === 'Moderate' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {results.risk} Risk
                    </span>
                  </div>
                  <Progress value={results.similarity} className="h-2 mb-2 bg-slate-100 dark:bg-slate-800" />
                  <div className="flex justify-between text-xs text-slate-500 mt-2">
                    <span>Originality: {results.originality}%</span>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-2 gap-4">
                <Card className="border-slate-200 dark:border-slate-800">
                  <CardContent className="p-4 flex flex-col items-center text-center">
                    <span className="text-3xl font-bold text-slate-700 dark:text-slate-200">{results.matches.length}</span>
                    <span className="text-xs text-slate-500 mt-1 uppercase font-semibold">Matches</span>
                  </CardContent>
                </Card>
                <Card className="border-slate-200 dark:border-slate-800">
                  <CardContent className="p-4 flex flex-col items-center text-center">
                    <span className="text-3xl font-bold text-slate-700 dark:text-slate-200">{results.total_sources}</span>
                    <span className="text-xs text-slate-500 mt-1 uppercase font-semibold">Sources</span>
                  </CardContent>
                </Card>
              </div>

              {/* Matched Segments List */}
              {results.matches.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">Detected Matches</h3>
                  {results.matches.map((match: any) => (
                    <Card key={match.id} className="border-slate-200 dark:border-slate-800">
                      <CardHeader className="p-3 pb-0">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-red-600 bg-red-50 px-2 py-1 rounded border border-red-100 uppercase">
                            {match.match_type} MATCH
                          </span>
                          <span className="text-xs font-medium">{match.similarity_score}% Sim</span>
                        </div>
                      </CardHeader>
                      <CardContent className="p-3 pt-2">
                        <p className="text-sm mb-2 p-2 bg-slate-50 dark:bg-slate-900 rounded italic border border-slate-100">
                          "...{match.text_segment}..."
                        </p>
                        <div className="text-xs text-slate-500 mb-3 flex flex-col gap-1">
                          <strong>Source:</strong> {match.source_name}
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full gap-2 text-xs h-8"
                          disabled={isRewriting}
                          onClick={() => handleRewrite(match.id, match.text_segment)}
                        >
                          {isRewriting ? <div className="w-3 h-3 border-2 border-slate-600 border-t-transparent rounded-full animate-spin" /> : <Wand2 className="w-3 h-3" />}
                          Rewrite with AI
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          ) : null}
        </div>
      </main>
    </div>
  );
}
