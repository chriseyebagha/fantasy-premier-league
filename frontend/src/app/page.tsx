'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Target, Layout, ChevronDown, Home as HomeIcon } from 'lucide-react';
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
        setMetadata(await res.json());
      }
    } catch (err) {
      console.error('Failed to fetch metadata:', err);
    }
  };

  const fetchDashboard = async (gw?: string) => {
    setLoading(true);
    try {
      const url = gw ? `/fantasy/history/gw_${gw}.json` : `/fantasy/dashboard_data.json`;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Engine unreachable');
      const dashboardData = await res.json();
      setData(dashboardData);
      if (!gw) setSelectedGw(dashboardData.gameweek.toString());
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetadata();
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#07090f]">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center gap-6"
        >
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 border-4 border-emerald-500/20 rounded-full" />
            <div className="absolute inset-0 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          </div>
          <p className="text-slate-400 font-black tracking-[0.3em] text-[10px] uppercase animate-pulse">
            Syncing FPL Projections...
          </p>
        </motion.div>
      </div>
    );
  }

  if (error || !data || data.status === 'offline') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-[#07090f]">
        <div className="glass-card rounded-[32px] p-10 max-w-sm text-center border-white/5">
          <div className="bg-rose-500/10 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Target className="text-rose-500" size={32} />
          </div>
          <h2 className="text-2xl font-black text-white mb-2 uppercase tracking-tight">System Offline</h2>
          <p className="text-slate-400 text-xs mb-8 font-medium leading-relaxed">
            {error || 'The FPL Predictor Engine is currently offline for maintenance.'}
          </p>
          <button
            onClick={() => fetchDashboard()}
            className="w-full py-4 bg-white text-black rounded-2xl text-[11px] font-black tracking-widest transition-all hover:bg-slate-200 active:scale-95"
          >
            RETRY CONNECT
          </button>
        </div>
      </div>
    );
  }

  const accuracy = metadata?.[data.gameweek.toString()]?.efficiency;

  return (
    <main className="app-container" suppressHydrationWarning>
      <nav className="fixed top-8 left-8 z-50">
        <a href="https://chriseyebagha.com" className="group flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg glass-card flex items-center justify-center group-hover:bg-white/10 transition-colors">
            <HomeIcon size={14} className="text-slate-400 group-hover:text-white" />
          </div>
          <span className="text-[10px] font-black uppercase tracking-[0.4em] text-slate-500 group-hover:text-white transition-colors hidden md:block">
            Chris Eyebagha
          </span>
        </a>
      </nav>

      <section className="mt-20 flex flex-col items-center gap-12">
        {/* Header Stats */}
        <div className="flex flex-col items-center gap-6">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center"
          >
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-sm md:text-xl font-black uppercase tracking-[0.5em] text-white">
                Gameweek {data.gameweek}
              </h1>
              {accuracy !== undefined && (
                <div className="bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full flex items-center gap-1.5">
                  <TrendingUp size={10} className="text-emerald-400" />
                  <span className="text-[9px] font-black text-emerald-400 uppercase tracking-tight">
                    {accuracy}% Success
                  </span>
                </div>
              )}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card points-pill-horizontal border-white/10 whitespace-nowrap flex items-center justify-center"
          >
            <span className="text-[11px] font-black text-slate-500 uppercase tracking-[0.2em]">Projected Total</span>
            <span className="text-3xl font-black text-white mx-4">{Math.round(data.total_projected_points || 0)}</span>
            <span className="text-[11px] font-black text-slate-500 uppercase tracking-[0.2em]">Points</span>
          </motion.div>
        </div>

        <section className="w-full max-w-5xl mx-auto">
          <div className="flex items-center gap-10 mb-12 px-4">
            <div className="h-[1px] flex-1 bg-white/5" />
            <h2 className="text-xs md:text-sm font-black uppercase tracking-[0.5em] text-slate-400 flex items-center gap-4">
              Captain Options
            </h2>
            <div className="h-[1px] flex-1 bg-white/5" />
          </div>
          <CaptainSection captains={data.recommendations} gameweek={data.gameweek} />
        </section>

        {/* Pitch Dashboard */}
        <section className="w-full max-w-5xl mx-auto flex flex-col gap-8 pb-32">
          <div className="flex items-center gap-10 px-4">
            <div className="h-[1px] flex-1 bg-white/5" />
            <h2 className="text-xs md:text-sm font-black uppercase tracking-[0.5em] text-slate-400 flex items-center gap-4">
              Predicted Starting XI
            </h2>
            <div className="h-[1px] flex-1 bg-white/5" />
          </div>
          <PlayerDashboard
            squad={data.squad}
            bench={data.bench}
            gameweek={data.gameweek}
            optimized_squad={data.optimized_squad}
            captainId={data.recommendations.obvious?.id}
          />
        </section>
      </section>
    </main>
  );
}

// Minimal Icons for UI
const Star = ({ size, className }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
);
