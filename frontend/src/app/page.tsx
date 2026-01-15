'use client';

import { useEffect, useState } from 'react';
import CaptainSection from '../components/CaptainSection';
import PlayerDashboard from '../components/PlayerDashboard';

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<any>(null);
  const [selectedGw, setSelectedGw] = useState<string | null>(null);

  const fetchMetadata = async () => {
    try {
      const res = await fetch('/fantasy/history/metadata.json');
      if (res.ok) {
        const meta = await res.json();
        setMetadata(meta);
      }
    } catch (err) {
      console.error('Failed to fetch metadata:', err);
    }
  };

  const fetchDashboard = async (gw?: string) => {
    setLoading(true);
    try {
      const url = gw
        ? `/fantasy/history/gw_${gw}.json`
        : `/fantasy/dashboard_data.json`;

      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch dashboard data');
      const dashboardData = await res.json();
      setData(dashboardData);
      if (!gw) setSelectedGw(dashboardData.gameweek.toString());
    } catch (err: any) {
      setError(err.message);
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetadata();
    fetchDashboard();
  }, []);

  const handleGwChange = (gw: string) => {
    setSelectedGw(gw);
    // If it's the latest GW in metadata, we could fetch dashboard_data.json, 
    // but the history version is essentially the same.
    fetchDashboard(gw);
  };

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
            onClick={() => fetchDashboard()}
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
        - Includes a dropdown for historical selection
      */}
      <header className="flex flex-col items-center mt-8 mb-8 gap-3 relative">
        <div className="flex flex-col items-center">
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-center text-sm md:text-base font-black uppercase tracking-[0.3em] text-slate-800">
              GW {data.gameweek} Predictions
            </h1>
            {metadata?.[data.gameweek.toString()]?.efficiency !== undefined && (
              <span className="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-[8px] font-black uppercase tracking-widest rounded-full border border-emerald-200">
                {metadata[data.gameweek.toString()].efficiency}% Accuracy
              </span>
            )}
          </div>

          <div className="flex items-center gap-4">
            <div className="flex flex-col items-center">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Total Projected</span>
              <span className="text-lg font-black text-indigo-600">
                {data.total_projected_points || '0.0'} pts
              </span>
            </div>
          </div>

          {selectedGw && metadata && selectedGw !== Object.keys(metadata).sort((a, b) => Number(b) - Number(a))[0] && (
            <span className="mt-2 px-2 py-0.5 bg-amber-100 text-amber-700 text-[8px] font-black uppercase tracking-widest rounded-full border border-amber-200 animate-pulse">
              Historical View
            </span>
          )}
        </div>

        {metadata && Object.keys(metadata).length > 0 && (
          <div className="flex items-center gap-3 bg-white/50 backdrop-blur-sm border border-slate-100 p-1 pl-3 rounded-full shadow-sm">
            <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
              Choose Week:
            </span>
            <select
              id="gw-select"
              value={selectedGw || ''}
              onChange={(e) => handleGwChange(e.target.value)}
              className="bg-slate-50 border-none rounded-full px-4 py-1.5 text-[10px] font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all cursor-pointer hover:bg-slate-100"
            >
              {/* Show Live Option */}
              <option value={Object.keys(metadata).sort((a, b) => Number(b) - Number(a))[0]}>
                GW {Object.keys(metadata).sort((a, b) => Number(b) - Number(a))[0]} (Live)
              </option>

              {/* Show History Options */}
              {Object.keys(metadata)
                .sort((a, b) => Number(b) - Number(a))
                .slice(1) // Skip the latest one as it's the 'Live' one
                .map(gw => (
                  <option key={gw} value={gw}>GW {gw}</option>
                ))
              }
            </select>
          </div>
        )}
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
