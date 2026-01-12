'use client';

import React from 'react';
import { Player } from '../types/player';

interface PlayerDashboardProps {
    squad: Player[];
    bench: Player[];
    gameweek?: number;
    weights?: any;
}

const PositionBadge = ({ position }: { position: number }) => {
    const labels: { [key: number]: string } = { 1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD' };
    const styles: { [key: number]: string } = {
        1: 'bg-yellow-400/20 text-yellow-400 border-yellow-400/30',
        2: 'bg-blue-400/20 text-blue-400 border-blue-400/30',
        3: 'bg-green-400/20 text-green-400 border-green-400/30',
        4: 'bg-red-400/20 text-red-400 border-red-400/30',
    };

    return (
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wider ${styles[position]}`}>
            {labels[position]}
        </span>
    );
};

const MiniPlayerCard = ({ player, isBench = false }: { player: any, isBench?: boolean }) => (
    <div className={`glass-card !p-0.5 md:!p-3 flex flex-col gap-0.5 md:gap-2 group animate-float ${isBench ? 'w-20 md:w-32 opacity-70 scale-95 border-white/5' : 'w-[17.5%] md:w-[130px] lg:w-[150px] flex-shrink-0 !bg-black/60 shadow-2xl'}`} style={{ animationDelay: `${Math.random() * 2}s` }}>
        <div className="flex justify-between items-start">
            <div className="w-full text-center md:text-right">
                <div className={`text-[8px] md:text-lg font-bold ${isBench ? 'text-slate-400' : 'text-primary-glow'}`}>{player.predicted_points.toFixed(1)}</div>
            </div>
        </div>

        <div className="text-center">
            <div className="font-black text-[6px] md:text-xs truncate uppercase tracking-tighter text-white/90">{player.web_name}</div>
            <div className="flex flex-col items-center gap-0.5 mt-0.5">
                <div className="text-[6px] md:text-[9px] text-text-muted leading-none whitespace-nowrap">
                    <span className="md:hidden">vs&nbsp;{player.next_fixture}</span>
                    <span className="hidden md:inline">{player.team} <span className="text-slate-400 font-normal ml-0.5 whitespace-nowrap">vs&nbsp;{player.next_fixture}</span></span>
                </div>

                <div
                    className="w-1 md:w-1.5 h-1 md:h-1.5 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.3)]"
                    style={{
                        backgroundColor: player.next_fixture_difficulty <= 2 ? '#10b981' :
                            player.next_fixture_difficulty <= 3 ? '#f59e0b' :
                                player.next_fixture_difficulty <= 4 ? '#f97316' : '#ef4444'
                    }}
                />
            </div>
        </div>

        {/* Real Stats Row - Hidden on Mobile */}
        <div className="hidden md:grid grid-cols-3 gap-1 py-1 border-y border-white/5 my-1">
            <div className="text-[8px] flex flex-col items-center">
                <span className="text-text-muted uppercase text-[7px] leading-tight">Goals/Asst</span>
                <span className="text-slate-900 font-bold">{player.goals}/{player.assists}</span>
            </div>
            <div className="text-[8px] flex flex-col items-center border-l border-white/5">
                <span className="text-text-muted uppercase text-[7px] leading-tight">xG/xA</span>
                <span className="text-slate-500">{player.xG}/{player.xA}</span>
            </div>
            <div className="text-[8px] flex flex-col items-center border-l border-white/5">
                <span className="text-text-muted uppercase text-[7px] leading-tight">Avg Min</span>
                <span className={`font-bold ${player.avg_minutes < 65 ? 'text-red-400' : 'text-green-400'}`}>
                    {player.avg_minutes}
                </span>
            </div>
        </div>

        <div className="hidden md:flex mt-auto pt-1 flex-col gap-1">
            <div className="flex justify-between items-center">
                <div className="text-[9px] text-text-muted uppercase font-medium">Price <span className="text-slate-700">£{player.price.toFixed(1)}m</span></div>
                <div className="text-[9px] text-text-muted uppercase font-medium">TSB <span className="text-slate-700">{player.ownership}%</span></div>
            </div>
            <div className="flex justify-between items-center pt-1 border-t border-white/5">
                <span className="text-[8px] text-text-muted uppercase tracking-wider">Explosivity</span>
                <div className="text-[10px] font-bold text-explosive-glow">{player.explosivity.toFixed(0)}%</div>
            </div>
        </div>
    </div>
);

export default function PlayerDashboard({ squad, bench, gameweek, weights, optimized_squad }: PlayerDashboardProps & { optimized_squad?: any }) {
    // Use optimized squad if available, otherwise fallback to top-15
    const displaySquad = optimized_squad?.players?.starting_11 || squad;
    const displayBench = optimized_squad?.players?.bench || bench;
    const formation = optimized_squad?.formation || "Top 15";

    if (!displaySquad) return null;

    // Group Starters by position
    const gks = displaySquad.filter((p: any) => p.position === 1);
    const defs = displaySquad.filter((p: any) => p.position === 2);
    const mids = displaySquad.filter((p: any) => p.position === 3);
    const fwds = displaySquad.filter((p: any) => p.position === 4);

    return (
        <div className="space-y-16">
            <div className="max-w-4xl mx-auto px-4 md:px-0">
                <h2 className="text-[10px] sm:text-sm md:text-2xl font-black uppercase tracking-widest sm:tracking-[0.3em] md:tracking-[0.5em] text-slate-800 text-center leading-relaxed mb-12">
                    Gameweek {gameweek || '22'} Team Selection
                </h2>
            </div>

            <div className="pitch-container relative overflow-visible !mt-0">
                <div className="absolute -top-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3 w-full pointer-events-none">
                    {optimized_squad && (
                        <div className="px-3 py-1 bg-primary-glow/10 border border-primary-glow/20 rounded-full text-[9px] font-bold text-primary-glow uppercase tracking-widest">
                            Formation {formation}
                        </div>
                    )}
                </div>

                {/* Forwards */}
                <div className="pitch-row">
                    {fwds.map((p: any) => <MiniPlayerCard key={p.id} player={p} />)}
                </div>

                {/* Midfielders */}
                <div className="pitch-row">
                    {mids.map((p: any) => <MiniPlayerCard key={p.id} player={p} />)}
                </div>

                {/* Defenders */}
                <div className="pitch-row">
                    {defs.map((p: any) => <MiniPlayerCard key={p.id} player={p} />)}
                </div>

                {/* Goalie */}
                <div className="pitch-row">
                    {gks.map((p: any) => <MiniPlayerCard key={p.id} player={p} />)}
                </div>
            </div>

            {/* Bench Row */}
            <div className="max-w-4xl mx-auto">
                <div className="flex items-center gap-4 mb-8">
                    <div className="h-[1px] flex-1 bg-slate-200/50" />
                    <h3 className="text-xs md:text-sm font-black uppercase tracking-[0.3em] text-slate-400">Substitutes</h3>
                    <div className="h-[1px] flex-1 bg-slate-200/50" />
                </div>
                <div className="flex flex-wrap justify-center gap-3 md:gap-8 hover:brightness-110 transition-all">
                    {displayBench?.map((p: any) => <MiniPlayerCard key={p.id} player={p} isBench />)}
                </div>
            </div>

            <div className="max-w-xl mx-auto mt-12">
                {/* Budget & Performance Card - Optimized Real Estate */}
                {optimized_squad && (
                    <div className="glass-card !bg-slate-50/50 border-t-2 border-slate-200 !p-4 md:!p-6">
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-8 md:gap-x-16">
                            <div className="flex flex-col">
                                <span className="text-[8px] uppercase font-black tracking-widest text-text-muted mb-1.5 md:mb-2">Team Cost</span>
                                <span className="text-[10px] md:text-sm font-bold text-slate-800">£{optimized_squad.total_cost}m <span className="text-slate-400 font-medium">/ £100m</span></span>
                            </div>
                            <div className="flex flex-col border-l border-slate-200/30 pl-8 md:pl-12">
                                <span className="text-[8px] uppercase font-black tracking-widest text-text-muted mb-1.5 md:mb-2">Projected XI</span>
                                <span className="text-[10px] md:text-sm font-bold text-explosive-glow">{optimized_squad.total_predicted_points?.toFixed(1) || '0.0'} <span className="text-[8px] md:text-[10px] uppercase ml-0.5">Pts</span></span>
                            </div>
                            <div className="flex flex-col border-l border-slate-200/30 pl-8 md:pl-12 hidden md:flex">
                                <span className="text-[8px] uppercase font-black tracking-widest text-text-muted mb-1.5 md:mb-2">Bench Potential</span>
                                <span className="text-[10px] md:text-sm font-bold text-slate-500">{optimized_squad.bench_predicted_points?.toFixed(1) || '0.0'} <span className="text-[8px] md:text-[10px] uppercase ml-0.5">Pts</span></span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
