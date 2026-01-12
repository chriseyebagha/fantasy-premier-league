'use client';

import React from 'react';

interface Captain {
    web_name: string;
    team: string; // Still kept for fallback
    next_fixture?: string; // Added next_fixture
    predicted_points: number;
    explosivity: number;
    ownership: number;
    reason?: string;
}

interface CaptainSectionProps {
    captains: {
        obvious: Captain;
        joker: Captain;
        fun_one: Captain;
        weights?: any;
    };
    gameweek: number;
}

const CaptainCard = ({ type, subtitle, data, glowClass }: { type: string, subtitle: string, data: Captain, glowClass: string }) => {
    if (!data) return null;

    return (
        <div className={`glass-card flex-1 min-w-0 md:w-full max-w-[320px] border-t-4 ${glowClass} !p-3 md:!p-4 shadow-sm hover:shadow-md transition-all flex flex-col`}>
            {/* Header: Label & Points */}
            <div className="flex justify-between items-start mb-2">
                <div className="min-w-0 flex-1">
                    <span className="text-[9px] md:text-[10px] font-black uppercase tracking-widest text-text-muted mb-0.5 block truncate">
                        {subtitle}
                    </span>
                    <h3 className="text-sm md:text-xl font-bold truncate leading-tight">{data.web_name || 'N/A'}</h3>
                </div>
                <div className="text-right ml-2 bg-slate-100/50 px-1.5 py-0.5 rounded">
                    <div className="text-lg md:text-2xl font-black text-slate-900 leading-none">
                        {(data.predicted_points || 0).toFixed(1)}
                    </div>
                </div>
            </div>

            {/* Context: Opponent */}
            <div className="mb-3">
                <div className="text-[10px] md:text-xs font-medium text-slate-500 flex items-center gap-1">
                    <span className="uppercase text-[9px] tracking-wider text-text-muted">vs</span>
                    <span className="text-slate-800 font-bold bg-white/60 px-1 rounded">{data.next_fixture || 'Unknown'}</span>
                </div>
            </div>

            {/* Stats Grid - Uniform Height Spacer */}
            <div className="mt-auto space-y-2 pt-2 border-t border-slate-100">
                <div className="flex justify-between items-center text-[10px]">
                    <span className="text-text-muted uppercase font-bold tracking-tighter text-[9px]">Explosivity</span>
                    <span className={`font-bold ${data.explosivity > 50 ? 'text-explosive-glow' : 'text-slate-700'}`}>
                        {(data.explosivity || 0).toFixed(0)}%
                    </span>
                </div>

                <div className="flex justify-between text-[10px]">
                    <span className="text-text-muted uppercase font-bold tracking-tighter text-[9px]">Ownership</span>
                    <span className="font-bold">{typeof data.ownership === 'number' ? data.ownership.toFixed(1) : (data.ownership || '0')}%</span>
                </div>
            </div>
        </div>
    );
};

export default function CaptainSection({ captains, gameweek }: CaptainSectionProps) {
    if (!captains) return null;

    return (
        <section className="mb-8">
            <div className="mb-4 flex items-center gap-3">
                <span className="bg-slate-800 text-white px-2 py-0.5 rounded text-[10px] font-black tracking-widest uppercase">GW {gameweek}</span>
                <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400">
                    Captaincy
                </h2>
            </div>

            <div className="flex flex-nowrap justify-between md:justify-center gap-2 md:gap-8 pb-4 px-1 md:px-0">
                <CaptainCard
                    type="obvious"
                    subtitle="Safe Pick"
                    data={captains.obvious}
                    glowClass="border-primary-glow"
                />
                <CaptainCard
                    type="joker"
                    subtitle="Differential"
                    data={captains.joker}
                    glowClass="border-joker-glow"
                />
                <CaptainCard
                    type="fun"
                    subtitle="Chaos Mode"
                    data={captains.fun_one}
                    glowClass="border-explosive-glow"
                />
            </div>

            {/* Premium Legend */}
            <div className="flex flex-wrap justify-center gap-x-6 gap-y-2 mt-2 px-4 py-3 bg-white/40 rounded-xl backdrop-blur-sm border border-white/20">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-primary-glow shadow-[0_0_8px_#6366f1]"></div>
                    <div className="flex flex-col">
                        <span className="text-[10px] font-bold text-slate-700 leading-none">Safe</span>
                        <span className="text-[8px] text-text-muted uppercase tracking-tight">Reliable Points</span>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-joker-glow shadow-[0_0_8px_#8b5cf6]"></div>
                    <div className="flex flex-col">
                        <span className="text-[10px] font-bold text-slate-700 leading-none">Diff</span>
                        <span className="text-[8px] text-text-muted uppercase tracking-tight">High Risk/Reward</span>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-explosive-glow shadow-[0_0_8px_#f43f5e]"></div>
                    <div className="flex flex-col">
                        <span className="text-[10px] font-bold text-slate-700 leading-none">Chaos</span>
                        <span className="text-[8px] text-text-muted uppercase tracking-tight">Pure Volatility</span>
                    </div>
                </div>
            </div>
        </section>
    );
}
