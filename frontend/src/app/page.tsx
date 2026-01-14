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
            Engine is Computing...
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
      {/* 
        HOME BUTTON
        - Absolute Top Left
        - Clean text only, no borders, no heavy background
      */}
      <a
        href="https://chriseyebagha.com"
        className="fixed top-6 left-6 z-50 group px-2 py-1"
      >
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-300 group-hover:text-slate-500 transition-colors shadow-sm">
          Home
        </span>
      </a>

      {/* 
        GW PREDICTIONS HEADER
        - Scaled up to match section headers
        - No pill, just clean bold text
      */}
      <header className="flex justify-center mt-8 mb-8">
        <h1 className="text-center text-sm md:text-base font-black uppercase tracking-[0.3em] text-slate-800">
          GW {data.gameweek} Predictions
        </h1>
      </header>

      {/* SECTION TITLE: Captain Options */}
      <h2 className="text-center text-xs md:text-sm font-black uppercase tracking-[0.2em] text-slate-400 mb-4">
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
      <h2 className="text-center text-xs md:text-sm font-black uppercase tracking-[0.2em] text-slate-400 mb-2 mt-2">
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
