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
        easy_choice: Captain;
        obvious: Captain;
        joker: Captain;
        fun_one: Captain;
        weights?: any;
    };
}

const CaptainCard = ({ type, data, glowClass }: { type: string, data: Captain, glowClass: string }) => {
    if (!data) return null;

    return (
        <div className={`glass-card flex-1 min-w-[240px] border-t-4 ${glowClass} !p-4`}>
            <div className="flex justify-between items-start mb-3">
                <div className="min-w-0">
                    <span className="text-[9px] font-black uppercase tracking-[0.2em] text-text-muted mb-0.5 block">
                        {type}
                    </span>
                    <h3 className="text-lg font-bold truncate">{data.web_name || 'N/A'}</h3>
                    <p className="text-text-muted text-[10px] uppercase font-medium">{data.team || 'Unknown'}</p>
                </div>
                <div className="text-right ml-2">
                    <div className="text-xl font-black text-slate-900 leading-none">
                        {(data.predicted_points || 0).toFixed(1)}
                    </div>
                    <div className="text-[8px] uppercase text-text-muted font-bold tracking-tighter">Exp Pts</div>
                </div>
            </div>

            <div className="space-y-3">
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
                <div className="h-[1px] flex-1 bg-slate-200" />
            </h2>
            <div className="flex flex-nowrap overflow-x-auto pb-4 gap-4 no-scrollbar -mx-2 px-2 items-stretch">
                <CaptainCard
                    type="The Easy Choice"
                    data={captains.easy_choice}
                    glowClass="border-fun-glow"
                />
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
        </section>
    );
}
