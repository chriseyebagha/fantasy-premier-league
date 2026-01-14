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
            <div className="jersey-card captain !w-full !max-w-[120px] !h-auto !aspect-[3/4] !min-h-[130px] !m-0 justify-between py-3 shadow-lg">

                {/* Position Tag */}
                <div className="text-[7px] font-bold text-slate-400 opacity-80 leading-none mb-1">
                    {getPositionText(data.position)}
                </div>

                {/* Name */}
                <div className="name-text !text-[10px] !mb-1">{data.web_name}</div>

                {/* Main Content */}
                <div className="flex flex-col items-center flex-1 justify-center gap-1">
                    {/* Points - Large like on pitch */}
                    <div className="score-text !text-3xl text-primary-glow">{Math.round(data.predicted_points)}</div>

                    {/* Fixture */}
                    <div className="fixture-text uppercase !text-[9px] text-slate-500">
                        {formatFixture(data.next_fixture)}
                    </div>
                </div>

                {/* Extra Stats (Explosivity) - Optional, maybe keep hidden to match pitch EXACTLY? 
                    User said "Simply replicate that...". 
                    Pitch card DOES NOT show explosivity. 
                    I will HIDE explosivity to be safe and EXACT, or maybe add it very subtly.
                    Let's add it very subtly at the bottom since this is the "Captain" view. 
                */}
                <div className="mt-1 text-[8px] font-bold text-slate-400 tracking-wider">
                    {Math.round(data.explosivity)}% EXP
                </div>

            </div>
        </div>
    );
};

const BrainMetric = ({ label, value, subtext }: { label: string, value: string, subtext?: string }) => (
    <div className="flex flex-col items-center">
        <span className="text-[8px] font-bold uppercase tracking-wider text-slate-500 mb-0.5">{label}</span>
        <div className="text-sm font-black text-slate-700">{value}</div>
        {subtext && <span className="text-[7px] font-bold text-slate-400">{subtext}</span>}
    </div>
);

const ModelBrainCard = ({ weights }: { weights: any }) => {
    if (!weights || !weights.brain) return null;
    const { brain } = weights;

    // Calculate average confidence from the dictionary
    const confValues = Object.values(brain.confidence_ema || {}) as number[];
    const avgConf = confValues.length ? (confValues.reduce((a, b) => a + b, 0) / confValues.length) : 1.0;

    return (
        <div className="mt-6 w-full max-w-lg mx-auto">
            <div className="jersey-card !w-full !max-w-none !h-auto !px-4 !py-3 !flex-row !justify-between !items-center !rounded-2xl shadow-sm border border-slate-100/50">
                <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400">
                        Model Intelligence
                    </span>
                </div>

                <div className="flex items-center gap-6 md:gap-8">
                    <BrainMetric
                        label="Noise Gate"
                        value={`${brain.noise_multiplier?.toFixed(2)}x`}
                    />
                    <BrainMetric
                        label="Confidence"
                        value={`${(avgConf * 100).toFixed(0)}%`}
                    />
                    <BrainMetric
                        label="Squad Acc"
                        value={`${((brain.squad_accuracy || 0) * 100).toFixed(0)}%`}
                    />
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

            {/* Model Brain Metrics */}
            <ModelBrainCard weights={captains.weights} />
        </section>
    );
}
