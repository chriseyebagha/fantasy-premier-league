'use client';

import React from 'react';

interface Captain {
    web_name: string;
    team: string;
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
}

const CaptainCard = ({ type, data, glowClass }: { type: string, data: Captain, glowClass: string }) => {
    if (!data) return null;

    return (
        <div className={`glass-card flex-1 min-w-0 md:w-full max-w-[320px] border-t-4 ${glowClass} !p-2 md:!p-4 shadow-sm hover:shadow-md transition-all`}>
            <div className="flex justify-between items-start mb-2 md:mb-3">
                <div className="min-w-0 flex-1">
                    <span className="text-[7px] md:text-[9px] font-black uppercase tracking-[0.2em] text-text-muted mb-0.5 block truncate">
                        {type.replace('The ', '')}
                    </span>
                    <h3 className="text-xs md:text-lg font-bold truncate">{data.web_name || 'N/A'}</h3>
                    <p className="text-text-muted text-[8px] md:text-[10px] uppercase font-medium truncate">{data.team || 'Unknown'}</p>
                </div>
                <div className="text-right ml-1 md:ml-2">
                    <div className="text-sm md:text-xl font-black text-slate-900 leading-none">
                        {(data.predicted_points || 0).toFixed(1)}
                    </div>
                </div>
            </div>

            <div className="space-y-3 hidden md:block">
                <div className="flex justify-between items-center text-[10px]">
                    <span className="text-text-muted uppercase font-bold tracking-tighter">Explosivity</span>
                    <div className="flex items-center gap-2">
                        <div className="h-1 w-16 bg-slate-200 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-1000 ${glowClass.replace('border-', 'bg-').replace('-glow', '')}`}
                                style={{ width: `${data.explosivity || 0}%` }}
                            />
                        </div>
                        <span className="font-bold">{(data.explosivity || 0).toFixed(0)}</span>
                    </div>
                </div>

                <div className="flex justify-between text-[10px]">
                    <span className="text-text-muted uppercase font-bold tracking-tighter">Ownership</span>
                    <span className="font-bold">{typeof data.ownership === 'number' ? data.ownership.toFixed(1) : (data.ownership || '0')}%</span>
                </div>

                {data.reason && (
                    <p className="text-[9px] text-text-muted italic leading-tight border-l-2 border-slate-200 pl-2">
                        "{data.reason}"
                    </p>
                )}
            </div>
        </div>
    );
};

export default function CaptainSection({ captains }: CaptainSectionProps) {
    if (!captains) return null;

    return (
        <section className="mb-8">
            <h2 className="text-[10px] font-black uppercase tracking-[0.4em] text-slate-400 mb-4 flex items-center gap-4">
                Recommended Selections
            </h2>
            <div className="flex flex-nowrap justify-between md:justify-center gap-2 md:gap-8 pb-4 px-1 md:px-0">
                <CaptainCard
                    type="The Obvious One"
                    data={captains.obvious}
                    glowClass="border-primary-glow"
                />
                <CaptainCard
                    type="The Joker"
                    data={captains.joker}
                    glowClass="border-joker-glow"
                />
                <CaptainCard
                    type="The Fun One"
                    data={captains.fun_one}
                    glowClass="border-explosive-glow"
                />
            </div>

            {/* Legend */}
            <div className="flex justify-center gap-4 md:gap-8 mt-2 px-2">
                <div className="flex items-center gap-1.5 opacity-80">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary-glow"></div>
                    <span className="text-[9px] text-text-muted font-medium uppercase tracking-tight">Obvious: Reliable & Safe</span>
                </div>
                <div className="flex items-center gap-1.5 opacity-80">
                    <div className="w-1.5 h-1.5 rounded-full bg-joker-glow"></div>
                    <span className="text-[9px] text-text-muted font-medium uppercase tracking-tight">Joker: High Risk/Reward</span>
                </div>
                <div className="flex items-center gap-1.5 opacity-80">
                    <div className="w-1.5 h-1.5 rounded-full bg-explosive-glow"></div>
                    <span className="text-[9px] text-text-muted font-medium uppercase tracking-tight">Fun: Pure Chaos</span>
                </div>
            </div>
        </section>
    );
}
