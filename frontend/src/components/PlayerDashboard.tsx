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
    <div className={`jersey-card ${isBench ? 'bench' : ''} ${isCaptain ? 'captain' : ''}`}>
        {isCaptain && <div className="captain-badge">C</div>}

        <div className="absolute top-[2px] left-0 right-0 flex justify-center text-[7px] font-bold text-slate-400 opacity-80 leading-none z-10">
            {getPositionText(player.element_type || player.position)}
        </div>

        <div className="name-text mt-2">{player.web_name}</div>

        <div className="flex flex-col items-center">
            <div className="score-text text-primary-glow">{Math.round(player.predicted_points)}</div>
            <div className="fixture-text uppercase">{formatFixture(player.next_fixture)}</div>
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
