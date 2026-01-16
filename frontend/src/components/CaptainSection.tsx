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

interface CaptainJerseyCardProps {
    subtitle: string;
    data: Captain;
    icon: any;
    color: string;
    description: string;
}

const CaptainJerseyCard = ({ subtitle, data, color, description }: any) => {
    if (!data) return null;

    const imageUrl = `https://resources.premierleague.com/premierleague/photos/players/250x250/p${data.code}.png`;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -8 }}
            className="flex flex-col items-center gap-2 w-full"
        >
            {/* Title + Description Header */}
            <div className="flex flex-col items-center text-center mb-1 w-full px-1">
                <span className="text-[10px] md:text-xs font-extrabold uppercase tracking-[0.15em] text-white/80">{subtitle}</span>
                <span className="text-[8px] md:text-[11px] font-medium text-slate-500 leading-tight mt-0.5 max-w-[120px] md:max-w-[180px]">{description}</span>
            </div>

            <div className="relative w-full max-w-[160px] md:max-w-[200px] group">
                {/* Captain Glow Effect */}
                <div className="captain-glow opacity-0 group-hover:opacity-40 transition-opacity duration-500" />

                <div className="glass-card rounded-[24px] overflow-hidden flex flex-col p-4 border border-white/5 relative z-10 transition-colors group-hover:border-white/20">
                    <div className="relative w-full aspect-square mb-2 -mt-2">
                        <img
                            src={imageUrl}
                            alt={data.web_name}
                            className="w-full h-full object-contain filter drop-shadow(0 8px 12px rgba(0,0,0,0.4)) group-hover:scale-110 transition-transform duration-500"
                            onError={(e) => {
                                (e.target as HTMLImageElement).src = 'https://resources.premierleague.com/premierleague/photos/players/250x250/Photo-Missing.png';
                            }}
                        />
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

                        <div className="flex items-center justify-center gap-1.5">
                            <span className="text-2xl font-black text-emerald-400">
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
            <div className="grid grid-cols-3 gap-2 md:gap-4 max-w-3xl mx-auto px-4">
                <CaptainJerseyCard
                    subtitle="The Obvious One"
                    data={captains.obvious}
                    color="text-amber-400"
                    description="Safe pick. High ownership, proven performer—if he hauls, you're covered."
                />
                <CaptainJerseyCard
                    subtitle="The Joker"
                    data={captains.joker}
                    color="text-violet-400"
                    description="Differential pick. Low ownership—if he hauls, you climb the ranks."
                />
                <CaptainJerseyCard
                    subtitle="The Fun One"
                    data={captains.fun_one}
                    color="text-rose-400"
                    description="Wild card. Defender with explosive potential for a CS + attacking returns."
                />
            </div>
        </section>
    );
}
