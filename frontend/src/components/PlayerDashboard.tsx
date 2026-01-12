'use client';

import React from 'react';
import { Player } from '../types/player';

interface PlayerDashboardProps {
    squad: Player[];
    bench: Player[];
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
    <div className={`glass-card !p-3 flex flex-col gap-2 group animate-float ${isBench ? 'opacity-70 scale-95 border-white/5' : 'min-w-[130px] max-w-[150px] !bg-black/60 shadow-2xl'}`} style={{ animationDelay: `${Math.random() * 2}s` }}>
        <div className="flex justify-between items-start">
            <PositionBadge position={player.position} />
            <div className="text-right">
                <div className={`text-lg font-bold ${isBench ? 'text-slate-400' : 'text-primary-glow'}`}>{player.predicted_points.toFixed(1)}</div>
            </div>
        </div>

        <div className="text-center">
            <div className="font-bold text-xs truncate uppercase tracking-tighter">{player.web_name}</div>
            <div className="flex flex-col items-center gap-0.5 mt-0.5">
                <div className="text-[9px] text-text-muted leading-none">{player.team}</div>
                <div className="flex items-center gap-1 mt-1">
                    <span className="text-[8px] font-black py-0.5 px-1.5 rounded bg-slate-100 border border-slate-200 text-slate-600">
                        {player.position}
                    </span>
                    <div
                        className="w-1.5 h-1.5 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.3)]"
                        style={{
                            backgroundColor: player.next_fixture_difficulty <= 2 ? '#10b981' :
                                player.next_fixture_difficulty <= 3 ? '#f59e0b' :
                                    player.next_fixture_difficulty <= 4 ? '#f97316' : '#ef4444'
                        }}
                    />
                </div>
            </div>
        </div>

        {/* Real Stats Row */}
        <div className="grid grid-cols-3 gap-1 py-1 border-y border-white/5 my-1">
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

        <div className="mt-auto pt-1 flex flex-col gap-1">
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

export default function PlayerDashboard({ squad, bench, weights, optimized_squad }: PlayerDashboardProps & { optimized_squad?: any }) {
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
            <div className="pitch-container relative overflow-visible">
                <div className="absolute -top-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1">
                    <div className="text-[10px] font-black tracking-[0.4em] text-slate-300 uppercase pointer-events-none">
                        Neural Team Architecture
                    </div>
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
            <div className="relative">
                <div className="flex items-center gap-4 mb-6">
                    <h3 className="text-xs font-bold uppercase tracking-widest text-text-muted">Substitutes</h3>
                    <div className="h-[1px] flex-1 bg-white/5" />
                </div>
                <div className="flex flex-wrap justify-center gap-6">
                    {displayBench?.map((p: any) => <MiniPlayerCard key={p.id} player={p} isBench />)}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
                {/* Budget & Performance Card */}
                {optimized_squad && (
                    <div className="glass-card border-l-4 border-explosive-glow">
                        <h3 className="text-sm font-bold mb-4 uppercase tracking-widest flex items-center gap-2">
                            Economic Efficiency Auditor
                        </h3>
                        <div className="space-y-3">
                            <div className="flex justify-between text-xs">
                                <span className="text-text-muted">Total Squad Cost</span>
                                <span className="font-mono text-slate-800">£{optimized_squad.total_cost}m / £100m</span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-text-muted">Projected Points (XI)</span>
                                <span className="font-mono text-explosive-glow">{optimized_squad.starting_11_points}</span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-text-muted">Bench Points potential</span>
                                <span className="font-mono text-slate-400">{optimized_squad.bench_points}</span>
                            </div>
                            <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden mt-2">
                                <div
                                    className="h-full bg-explosive-glow shadow-[0_0_8px_#f97316]"
                                    style={{ width: `${(optimized_squad.total_cost / 100) * 100}%` }}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Weights Card */}
                <div className="glass-card border-l-4 border-primary-glow">
                    <h3 className="text-sm font-bold mb-4 uppercase tracking-widest flex items-center gap-2">
                        Algorithm Weights Auditor
                    </h3>
                    <div className="space-y-3">
                        <div className="flex justify-between text-xs">
                            <span className="text-text-muted">Form Coefficient</span>
                            <span className="font-mono text-primary-glow">×{weights?.form_weight || '0.70'}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                            <span className="text-text-muted">Difficulty Multiplier</span>
                            <span className="font-mono text-primary-glow">×{weights?.fdr_weight || '0.50'}</span>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}
