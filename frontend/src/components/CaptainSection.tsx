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

const CaptainCard = ({ subtitle, data, glowClass }: { subtitle: string, data: Captain, glowClass: string }) => {
    if (!data) return null;

    return (
        <div className={`glass-card flex-1 min-w-0 md:w-full max-w-[320px] border-t-4 ${glowClass} !p-4 md:!p-5 shadow-sm hover:shadow-xl transition-all flex flex-col hover:-translate-y-1`}>
            {/* Header: Label & Points */}
            <div className="flex justify-between items-start mb-3">
                <div className="min-w-0 flex-1">
                    <span className="text-[9px] md:text-[10px] font-black uppercase tracking-widest text-text-muted mb-1 block truncate">
                        {subtitle}
                    </span>
                    <h3 className="text-sm md:text-xl font-black text-slate-800 truncate leading-tight uppercase tracking-tight">{data.web_name || 'N/A'}</h3>
                </div>
                <div className="text-right ml-2 bg-slate-900 text-white px-2 py-1 rounded-lg shadow-lg shadow-slate-200">
                    <div className="text-lg md:text-2xl font-black leading-none">
                        {(data.predicted_points || 0).toFixed(1)}
                    </div>
                </div>
            </div>

            {/* Context: Opponent */}
            <div className="mb-4">
                <div className="text-[10px] md:text-xs font-bold text-slate-500 flex items-center gap-1.5">
                    <span className="uppercase text-[9px] tracking-widest text-text-muted font-bold tracking-tight">vs</span>
                    <span className="text-slate-900 bg-slate-100 px-2 py-0.5 rounded-md font-bold">{data.next_fixture || 'Unknown'}</span>
                </div>
            </div>

            {/* Stats Grid - Uniform Height Spacer */}
            <div className="mt-auto space-y-2.5 pt-3 border-t border-slate-100">
                <div className="flex justify-between items-center text-[10px]">
                    <span className="text-text-muted uppercase font-black tracking-widest text-[8px]">Explosivity</span>
                    <span className={`font-black ${data.explosivity > 50 ? 'text-explosive-glow' : 'text-slate-800'}`}>
                        {(data.explosivity || 0).toFixed(0)}%
                    </span>
                </div>

                <div className="flex justify-between text-[10px]">
                    <span className="text-text-muted uppercase font-black tracking-widest text-[8px]">Ownership</span>
                    <span className="font-black text-slate-800">{typeof data.ownership === 'number' ? data.ownership.toFixed(1) : (data.ownership || '0')}%</span>
                </div>
            </div>
        </div>
    );
};

export default function CaptainSection({ captains, gameweek }: CaptainSectionProps) {
    if (!captains) return null;

    return (
        <section className="mb-12 md:mb-20">
            <div className="mb-10 text-center md:text-left">
                <h2 className="text-sm md:text-xl font-black uppercase tracking-[0.4em] text-slate-800">
                    GW {gameweek} Captaincy
                </h2>
            </div>

            <div className="max-w-5xl mx-auto">
                <div className="flex flex-nowrap justify-center gap-4 md:gap-8 pb-8 px-1 md:px-0">
                    <CaptainCard
                        subtitle="Safe Pick"
                        data={captains.obvious}
                        glowClass="border-primary-glow"
                    />
                    <CaptainCard
                        subtitle="Differential"
                        data={captains.joker}
                        glowClass="border-joker-glow"
                    />
                    <CaptainCard
                        subtitle="Chaos Mode"
                        data={captains.fun_one}
                        glowClass="border-explosive-glow"
                    />
                </div>

                <div className="py-2" />
            </div>
        </section>
    );
}
