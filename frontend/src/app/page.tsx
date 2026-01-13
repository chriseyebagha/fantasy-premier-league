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
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-400 font-bold animate-pulse tracking-widest text-[10px] uppercase">
            Oracle is Computing...
          </p>
        </div>
      </div>
    );
  }

  if (error || !data || data.status === 'offline') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 text-center bg-bg-color">
        <div className="bg-white border-2 border-slate-100 rounded-3xl p-8 shadow-xl max-w-sm">
          <h2 className="text-xl font-black text-slate-800 mb-2">Engine Offline</h2>
          <p className="text-slate-400 text-xs mb-6 font-medium">{error || 'The FPL backend is currently disconnected.'}</p>
          <button
            onClick={fetchDashboard}
            className="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-full text-[10px] font-bold tracking-widest transition-all shadow-lg active:scale-95"
          >
            RETRY CONNECTION
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="app-container" suppressHydrationWarning>

      {/* 
        PREMIUM HEADER - THIN PILL 
        - Replicates the .jersey-card aesthetic (white, glass, blur, border)
        - Compact and clean.
      */}
      <header className="sticky top-2 z-50 flex justify-center mb-6 pointer-events-none">
        <div className="flex items-center gap-4 pointer-events-auto">
             <a 
                href="https://chriseyebagha.com" 
                className="jersey-card !w-auto !h-auto !px-4 !py-3 !rounded-2xl shadow-lg hover:scale-105 transition-transform group"
            >
               <span className="text-[10px] md:text-xs font-black uppercase tracking-widest text-slate-400 group-hover:text-slate-600 transition-colors">
                  ← Home
               </span>
            </a>
            <div className="jersey-card !w-auto !h-auto !max-w-none px-10 py-3 !aspect-auto !flex-row !gap-0 !rounded-2xl shadow-lg">
              <h1 className="text-[10px] md:text-xs font-black uppercase tracking-[0.2em] text-slate-500 leading-none">
                GW {data.gameweek} Predictions
              </h1>
            </div>
        </div>
      </header>

      {/* SECTION TITLE: Captain Options */}
      <h2 className="text-center text-[9px] md:text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 mb-4">
        Captain Options
      </h2>

      {/* 
        CAPTAINCY SECTION 
        - Zero overlap container
        - "Premium Control Deck"
      */}
      <section className="shrink-0 w-full max-w-5xl mx-auto">
        <CaptainSection captains={data.recommendations} gameweek={data.gameweek} />
      </section>

      {/* SECTION TITLE: Top predicted players */}
      <h2 className="text-center text-[9px] md:text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 mb-2 mt-2">
        Top predicted players
      </h2>

      {/* 
        THE PITCH 
        - Occupies remaining space
      */}
      <div className="w-full max-w-5xl mx-auto flex-1 flex flex-col min-h-0">
        <PlayerDashboard
          squad={data.squad}
          bench={data.bench}
          gameweek={data.gameweek}
          optimized_squad={data.optimized_squad}
          captainId={data.recommendations.obvious?.id}
        />
      </div>
    </main>
  );
}
