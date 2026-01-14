'use client';

import React from 'react';
import { formatFixture, getPositionText } from '../utils/fplUtils';

interface Captain {
    web_name: string;
    team: string;
    next_fixture?: string;
    predicted_points: number;
    explosivity: number;
    ownership: number;
    reason?: string;
    position: number; // element_type
    haul_prob?: number;
    haul_alert?: boolean;
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

// Replicating the exact structure of MiniPlayerCard from PlayerDashboard
const CaptainJerseyCard = ({ subtitle, data }: { subtitle: string, data: Captain }) => {
    if (!data) return null;

    return (
        <div className="flex flex-col items-center gap-2">

            {/* Category Label (Outside the card, clean text) */}
            <span className="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400">
                {subtitle}
            </span>

            {/* 
               The "Jersey Card" Pill.
               WE MUST OVERRIDE the global .jersey-card width/height/margin constraints 
               to make it work in this grid context.
               - !w-full !max-w-[100px]: Allow it to size to the grid but stop it from being huge
               - !h-auto !aspect-[3/4]: Maintain vertical rectangular pill shape
               - !m-0: Remove margins
            */}
            {/* 
               The "Jersey Card" Pill.
               WE MUST OVERRIDE the global .jersey-card width/height/margin constraints 
               to make it work in this grid context.
               - !w-full !max-w-[120px]: Increased width
               - !h-auto !aspect-[3/4]: Maintain vertical rectangular pill shape
               - !m-0: Remove margins
            */}
            <div className={`jersey-card captain relative !w-full !max-w-[120px] !h-auto !aspect-[3/4] !min-h-[130px] !m-0 justify-between py-3 shadow-lg transition-all duration-500 ${data.haul_alert ? 'border-orange-500/50 shadow-orange-500/20' : ''}`}>

                {/* Vesuvius Pulse Badge */}
                {data.haul_alert && (
                    <div className="absolute -top-1 -right-1 z-20 flex items-center gap-1 bg-gradient-to-r from-orange-600 to-red-600 rounded-full px-2 py-0.5 shadow-[0_0_15px_rgba(234,88,12,0.4)] animate-pulse border border-orange-400/30">
                        <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white fill-orange-200"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" /></svg>
                        <span className="text-[7px] font-black italic tracking-tighter text-white">VESUVIUS</span>
                    </div>
                )}

                {/* Position Tag */}
                <div className="text-[7px] font-bold text-slate-400 opacity-80 leading-none mb-1">
                    {getPositionText(data.position)}
                </div>

                {/* Name */}
                <div className="name-text !text-[10px] !mb-1">{data.web_name}</div>

                {/* Main Content */}
                <div className="flex flex-col items-center flex-1 justify-center gap-1">
                    {/* Points - Large like on pitch */}
                    <div className={`score-text !text-3xl transition-colors duration-500 ${data.haul_alert ? 'text-orange-400 drop-shadow-[0_0_8px_rgba(251,146,60,0.4)]' : 'text-primary-glow'}`}>
                        {Math.round(data.predicted_points)}
                    </div>

                    {/* Fixture */}
                    <div className="fixture-text uppercase !text-[9px] text-slate-500">
                        {formatFixture(data.next_fixture)}
                    </div>
                </div>

                {/* Extra Stats (Explosivity / Haul Prob) */}
                <div className="mt-1 flex flex-col items-center gap-0.5">
                    <div className="text-[8px] font-bold text-slate-400 tracking-wider">
                        {Math.round(data.explosivity)}% EXP
                    </div>
                    {data.haul_prob && data.haul_prob > 0 && (
                        <div className={`text-[7px] font-black tracking-widest px-1.5 py-0.5 rounded-full ${data.haul_alert ? 'bg-orange-500/10 text-orange-400' : 'text-slate-500 opacity-60'}`}>
                            {Math.round(data.haul_prob * 100)}% HAUL
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default function CaptainSection({ captains, gameweek }: CaptainSectionProps) {
    if (!captains) return null;

    return (
        <section className="w-full mb-6 md:mb-10">
            {/* Grid: 3 Columns, Side-by-Side on Mobile */}
            <div className="grid grid-cols-3 gap-1 md:gap-4 justify-items-center w-full max-w-lg mx-auto transform scale-110 origin-top">
                <CaptainJerseyCard
                    subtitle="Obvious"
                    data={captains.obvious}
                />
                <CaptainJerseyCard
                    subtitle="Joker"
                    data={captains.joker}
                />
                <CaptainJerseyCard
                    subtitle="Fun"
                    data={captains.fun_one}
                />
            </div>
        </section>
    );
}
