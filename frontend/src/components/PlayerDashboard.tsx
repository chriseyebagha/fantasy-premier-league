'use client';

import React from 'react';
import { Player } from '../types/player';

interface PlayerDashboardProps {
    squad: Player[];
    bench: Player[];
    gameweek?: number;
    captainId?: number;
    optimized_squad?: any;
}

import { formatFixture, getPositionText } from '../utils/fplUtils';

const MiniPlayerCard = ({ player, isBench = false, isCaptain = false }: { player: any, isBench?: boolean, isCaptain?: boolean }) => (
    <div className={`jersey-card relative ${isBench ? 'bench' : ''} ${isCaptain ? 'captain' : ''} ${player.haul_alert ? 'border-orange-500/50 shadow-[0_0_15px_rgba(234,88,12,0.15)]' : ''}`}>
        {isCaptain && <div className="captain-badge">C</div>}

        {/* Vesuvius Pulse Badge */}
        {player.haul_alert && (
            <div className="absolute -top-1 -right-1 z-20 flex items-center gap-1 bg-gradient-to-r from-orange-600 to-red-600 rounded-full px-1.5 py-0.5 shadow-[0_0_10px_rgba(234,88,12,0.4)] animate-pulse border border-orange-400/30">
                <svg xmlns="http://www.w3.org/2000/svg" width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white fill-orange-200"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" /></svg>
                <span className="text-[6px] font-black italic tracking-tighter text-white">VESUVIUS</span>
            </div>
        )}

        <div className="absolute top-[2px] left-0 right-0 flex justify-center text-[7px] font-bold text-slate-400 opacity-80 leading-none z-10">
            {getPositionText(player.element_type || player.position)}
        </div>

        <div className="name-text mt-2">{player.web_name}</div>

        <div className="flex flex-col items-center flex-1 justify-center">
            <div className={`score-text transition-colors duration-500 ${player.haul_alert ? 'text-orange-400 drop-shadow-[0_0_8px_rgba(251,146,60,0.4)]' : 'text-primary-glow'}`}>
                {Math.round(player.predicted_points)}
            </div>
            <div className="fixture-text uppercase">{formatFixture(player.next_fixture)}</div>

            {/* Haul Potential % Indicator */}
            {player.haul_prob !== undefined && player.haul_prob > 0 && (
                <div className={`text-[6px] font-black tracking-widest mt-0.5 px-1 rounded-full ${player.haul_alert ? 'bg-orange-500/10 text-orange-400' : 'text-slate-500 opacity-40'}`}>
                    {Math.round(player.haul_prob * 100)}% HAUL
                </div>
            )}
        </div>
    </div>
);

export default function PlayerDashboard({ squad, bench, gameweek, optimized_squad, captainId }: PlayerDashboardProps) {
    const displaySquad = optimized_squad?.players?.starting_11 || squad;
    const displayBench = optimized_squad?.players?.bench || bench;

    if (!displaySquad) return null;

    // Group Starters by position
    const gks = displaySquad.filter((p: any) => p.position === 1);
    const defs = displaySquad.filter((p: any) => p.position === 2);
    const mids = displaySquad.filter((p: any) => p.position === 3);
    const fwds = displaySquad.filter((p: any) => p.position === 4);

    return (
        <div className="pitch-area">
            {/* Forwards */}
            <div className="pitch-row">
                {fwds.map((p: any) => <MiniPlayerCard key={p.id} player={p} isCaptain={p.id === captainId} />)}
            </div>

            {/* Midfielders */}
            <div className="pitch-row">
                {mids.map((p: any) => <MiniPlayerCard key={p.id} player={p} isCaptain={p.id === captainId} />)}
            </div>

            {/* Defenders */}
            <div className="pitch-row">
                {defs.map((p: any) => <MiniPlayerCard key={p.id} player={p} isCaptain={p.id === captainId} />)}
            </div>

            {/* Goalie */}
            <div className="pitch-row">
                {gks.map((p: any) => <MiniPlayerCard key={p.id} player={p} isCaptain={p.id === captainId} />)}
            </div>

            {/* Bench */}
            <div className="bench-section mt-auto">
                <div className="bench-title">Substitutes</div>
                <div className="pitch-row">
                    {displayBench?.map((p: any) => <MiniPlayerCard key={p.id} player={p} isBench />)}
                </div>
            </div>
        </div>
    );
}
