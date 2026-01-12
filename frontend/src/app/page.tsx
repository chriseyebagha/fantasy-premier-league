'use client';

import { useEffect, useState } from 'react';
import CaptainSection from '../components/CaptainSection';
import PlayerDashboard from '../components/PlayerDashboard';

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const res = await fetch('/fantasy/dashboard_data.json');
      if (!res.ok) throw new Error('Failed to fetch dashboard data');
      const dashboardData = await res.json();
      setData(dashboardData);
    } catch (err: any) {
      setError(err.message);
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-color">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-glow border-t-transparent rounded-full animate-spin" />
          <p className="text-text-muted font-bold animate-pulse tracking-widest text-[10px] uppercase">
            Oracle is Computing...
          </p>
        </div>
      </div>
    );
  }

  if (error || !data || data.status === 'offline') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 text-center bg-bg-color">
        <div className="glass-card border-explosive-glow max-w-md p-8">
          <h2 className="text-2xl font-bold text-explosive-glow mb-2">Engine Offline</h2>
          <p className="text-text-muted text-sm mb-6">{error || 'The FPL backend is currently disconnected.'}</p>
          <button
            onClick={fetchDashboard}
            className="px-8 py-3 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded-full text-[10px] font-bold tracking-widest transition-all"
          >
            RETRY CONNECTION
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-bg-color text-text-color selection:bg-primary-glow/30" suppressHydrationWarning>
      {/* Premium Header */}
      <header className="sticky top-0 z-50 py-6 bg-bg-color/80 backdrop-blur-xl">
        <div className="container mx-auto px-6 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-black bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-500 uppercase tracking-tight">
              Gameweek {data.gameweek}
            </h1>
          </div>

          <div className="flex items-center gap-6">
            <nav className="hidden md:flex items-center gap-6 text-[10px] font-bold tracking-[0.2em] uppercase text-text-muted">
              <a
                href="https://github.com/chriseyebagha/fantasy-premier-league/blob/main/TECHNICAL_SPEC.md"
                target="_blank"
                className="hover:text-slate-900 transition-colors"
              >
                Technical Spec
              </a>
              <a
                href="https://github.com/chriseyebagha/fantasy-premier-league"
                target="_blank"
                className="hover:text-slate-900 transition-colors"
              >
                View Source
              </a>
            </nav>

            <button
              onClick={fetchDashboard}
              className="p-2.5 hover:bg-slate-100 rounded-full transition-all border border-transparent hover:border-slate-200"
              title="Refresh Engine"
            >
              <svg className="w-5 h-5 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-12">
        {/* Tiered Captains */}
        <section className="mb-20">
          <CaptainSection captains={data.recommendations} />
        </section>

        {/* Neural Squad */}
        <section className="mb-20">

          <PlayerDashboard
            squad={data.squad}
            bench={data.bench}
            optimized_squad={data.optimized_squad}
            weights={data.recommendations.weights}
          />
        </section>
      </div>

    </main>
  );
}
