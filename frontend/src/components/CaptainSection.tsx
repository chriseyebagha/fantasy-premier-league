'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Star, Zap, Crown, Flame } from 'lucide-react';
import { formatFixture, getPositionText } from '../utils/fplUtils';

interface Captain {
    id: number;
    code: number;
    web_name: string;
    team: string;
    position: number;
    predicted_points: number;
    next_fixture: string;
    haul_prob?: number;
    haul_alert?: boolean;
}

interface CaptainSectionProps {
    captains: {
        obvious: Captain;
        joker: Captain;
        fun_one: Captain;
    };
    gameweek: number;
}

const CaptainJerseyCard = ({ subtitle, data, icon: Icon, color }: { subtitle: string, data: Captain, icon: any, color: string }) => {
    if (!data) return null;

    const imageUrl = `https://resources.premierleague.com/premierleague/photos/players/250x250/p${data.code}.png`;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -8 }}
            className="flex flex-col items-center gap-3 w-full"
        >
            <div className="flex items-center gap-1.5 mb-1">
                <Icon size={14} className={color} />
                <span className="text-[10px] font-extrabold uppercase tracking-[0.2em] text-slate-400">{subtitle}</span>
            </div>

            <div className="relative w-full max-w-[160px] group">
                {/* Captain Glow Effect */}
                <div className="captain-glow opacity-0 group-hover:opacity-40 transition-opacity duration-500" />

                <div className="glass-card rounded-[24px] overflow-hidden flex flex-col p-4 border border-white/5 relative z-10 transition-colors group-hover:border-white/20">
                    <div className="relative w-full aspect-square mb-2 -mt-2">
                        <img
                            src={imageUrl}
                            alt={data.web_name}
                            className="w-full h-full object-contain filter drop-shadow(0 8px 12px rgba(0,0,0,0.4)) group-hover:scale-110 transition-transform duration-500"
                        />
                        <div className="absolute top-0 right-0">
                            <div className="bg-amber-500 text-black text-[10px] font-black w-6 h-6 rounded-lg flex items-center justify-center shadow-lg transform rotate-12 group-hover:rotate-0 transition-transform">
                                C
                            </div>
                        </div>
                    </div>

                    <div className="space-y-1">
                        <div className="flex justify-center gap-1.5">
                            <span className="bg-white/10 text-white/60 text-[8px] font-bold px-1.5 py-0.5 rounded-md">
                                {getPositionText(data.position)}
                            </span>
                        </div>

                        <h3 className="text-white font-bold text-sm text-center truncate uppercase tracking-tight">
                            {data.web_name}
                        </h3>

                        <div className="flex items-center justify-center gap-1">
                            <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-br from-emerald-400 to-teal-500">
                                {Math.round(data.predicted_points)}
                            </span>
                            <span className="text-[10px] font-bold text-slate-500 uppercase">xP</span>
                        </div>

                        <div className="text-[9px] font-semibold text-slate-500 text-center uppercase tracking-wide">
                            {formatFixture(data.next_fixture)}
                        </div>

                        {data.haul_prob && data.haul_prob > 0.25 && (
                            <div className="mt-2 flex items-center justify-center gap-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full py-1 px-2">
                                <Flame size={10} className="text-emerald-400 fill-emerald-400" />
                                <span className="text-[8px] font-black text-emerald-400 uppercase tracking-tighter">High Haul Chance</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default function CaptainSection({ captains, gameweek }: CaptainSectionProps) {
    if (!captains) return null;

    return (
        <section className="w-full py-8">
            <div className="grid grid-cols-3 gap-3 md:gap-8 max-w-4xl mx-auto px-4">
                <CaptainJerseyCard
                    subtitle="The Meta Pick"
                    data={captains.obvious}
                    icon={Star}
                    color="text-amber-400"
                />
                <CaptainJerseyCard
                    subtitle="The Risk Taker"
                    data={captains.joker}
                    icon={Zap}
                    color="text-violet-400"
                />
                <CaptainJerseyCard
                    subtitle="The Wildcard"
                    data={captains.fun_one}
                    icon={Crown}
                    color="text-rose-400"
                />
            </div>
        </section>
    );
}
