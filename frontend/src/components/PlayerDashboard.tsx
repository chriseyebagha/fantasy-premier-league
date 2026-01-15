'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Flame } from 'lucide-react';
import { Player } from '../types/player';
import { formatFixture, getPositionText } from '../utils/fplUtils';

interface PlayerDashboardProps {
    squad: Player[];
    bench: Player[];
    gameweek?: number;
    captainId?: number;
    optimized_squad?: any;
}

const MiniPlayerCard = ({ player, isBench = false, isCaptain = false }: { player: any, isBench?: boolean, isCaptain?: boolean }) => {
    const imageUrl = `https://resources.premierleague.com/premierleague/photos/players/250x250/p${player.code}.png`;
    const position = getPositionText(player.element_type || player.position);

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ scale: 1.05 }}
            className={`player-card-container ${isBench ? 'opacity-80 scale-90' : ''}`}
        >
            <div className="player-portrait-container">
                <img
                    src={imageUrl}
                    alt={player.web_name}
                    className="player-portrait"
                    onError={(e) => {
                        (e.target as HTMLImageElement).src = 'https://resources.premierleague.com/premierleague/photos/players/250x250/photoless.png';
                    }}
                />

                {isCaptain && (
                    <>
                        <div className="captain-glow" />
                        <div className="captain-badge-premium">C</div>
                    </>
                )}

                {player.haul_alert && (
                    <div className="absolute -top-2 -left-2 z-20">
                        <motion.div
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ repeat: Infinity, duration: 2 }}
                            className="bg-emerald-500 rounded-full p-1 shadow-lg shadow-emerald-500/50"
                        >
                            <Flame size={10} className="text-white fill-white" />
                        </motion.div>
                    </div>
                )}
            </div>

            <div className="player-info-box glass-card border-white/5 group-hover:border-white/20 transition-colors">
                <div className="text-[7px] font-black text-slate-500 uppercase tracking-tighter mb-0.5">
                    {position}
                </div>
                <div className="player-name">
                    {player.web_name}
                </div>
                <div className="flex items-center justify-center gap-1">
                    <span className="player-points">
                        {Math.round(player.predicted_points)}
                    </span>
                    <span className="text-[8px] font-bold text-slate-500 uppercase">xP</span>
                </div>
                <div className="player-fixture mt-0.5">
                    {formatFixture(player.next_fixture)}
                </div>
            </div>
        </motion.div>
    );
};

export default function PlayerDashboard({ squad, bench, gameweek, optimized_squad, captainId }: PlayerDashboardProps) {
    const displaySquad = optimized_squad?.players?.starting_11 || squad;
    const displayBench = optimized_squad?.players?.bench || bench;

    if (!displaySquad) return null;

    // Group Starters by position
    const gks = displaySquad.filter((p: any) => (p.element_type || p.position) === 1);
    const defs = displaySquad.filter((p: any) => (p.element_type || p.position) === 2);
    const mids = displaySquad.filter((p: any) => (p.element_type || p.position) === 3);
    const fwds = displaySquad.filter((p: any) => (p.element_type || p.position) === 4);

    // Calculate formation string (e.g., "4-4-2")
    const formation = `${defs.length}-${mids.length}-${fwds.length}`;

    return (
        <div className="w-full space-y-6">
            <div className="pitch-container glass-card">
                <div className="pitch-grid-lines" />

                {/* Formation Label */}
                <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20">
                    <div className="glass-pill px-4 py-1.5 rounded-full border-white/10">
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">
                            System: {formation}
                        </span>
                    </div>
                </div>

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
            </div>

            {/* Bench Section */}
            <div className="w-full max-w-4xl mx-auto space-y-2">
                <div className="flex items-center justify-center gap-3">
                    <div className="h-[1px] flex-1 bg-white/5" />
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Substitutes</span>
                    <div className="h-[1px] flex-1 bg-white/5" />
                </div>
                <div className="bench-tray glass-card border-white/5">
                    {displayBench?.map((p: any) => <MiniPlayerCard key={p.id} player={p} isBench />)}
                </div>
            </div>
        </div>
    );
}
