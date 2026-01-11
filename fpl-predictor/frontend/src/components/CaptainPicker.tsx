'use client';

import React, { useEffect, useState } from 'react';
import { ExtendedPlayer, formatPrice } from '../types/player';

interface CaptainPickerProps {
    mode?: 'standard' | 'joker';
}

const CaptainPicker: React.FC<CaptainPickerProps> = ({ mode = 'standard' }) => {
    const [players, setPlayers] = useState<ExtendedPlayer[]>([]);
    const [loading, setLoading] = useState(true);
    const [modelStatus, setModelStatus] = useState<any>(null);

    useEffect(() => {
        fetchData();
        fetchModelStatus();
    }, [mode]);

    const fetchModelStatus = async () => {
        try {
            const res = await fetch('http://localhost:5001/api/model-status');
            const data = await res.json();
            setModelStatus(data);
        } catch (e) {
            console.error("Error fetching model status", e);
        }
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            // Standard: All players, ranked by explosivity
            // Joker: < 20% ownership, ranked by explosivity
            const maxOwn = mode === 'joker' ? 20 : 100;

            const res = await fetch(`http://localhost:5001/api/jokers?top_n=20&max_ownership=${maxOwn}`);
            const data = await res.json();

            if (Array.isArray(data)) {
                setPlayers(data);
            } else {
                console.error('API returned invalid data:', data);
                setPlayers([]);
            }
        } catch (error) {
            console.error('Error fetching players:', error);
            setPlayers([]);
        } finally {
            setLoading(false);
        }
    };

    const getPositionName = (pos: number) => {
        switch (pos) {
            case 1: return 'GK';
            case 2: return 'DEF';
            case 3: return 'MID';
            case 4: return 'FWD';
            default: return 'UNK';
        }
    };

    if (loading) {
        return (
            <div className="space-y-4">
                <div className="h-16 bg-gray-100 rounded-xl animate-pulse" />
                <div className="h-96 bg-gray-100 rounded-xl animate-pulse" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header & Model Status */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-xl font-bold text-gray-900 tracking-tight">
                        {mode === 'standard' ? 'Explosivity Rankings' : 'Differential Picks (<20%)'}
                    </h2>
                    <p className="text-gray-500 text-sm mt-1">
                        {mode === 'standard'
                            ? 'All players ranked by their potential for massive hauls.'
                            : 'Low-owned players with high ceiling potential.'
                        }
                    </p>
                </div>

                {modelStatus && (
                    <div className="flex items-center gap-2 text-xs font-medium text-gray-500">
                        <span className={`w-2 h-2 rounded-full ${modelStatus.status === 'Healthy' ? 'bg-emerald-500' : 'bg-amber-500'
                            }`} />
                        {modelStatus.status}
                    </div>
                )}
            </div>

            <div className="linear-table-container">
                {/* Grid Header */}
                <div className="linear-header" style={{ gridTemplateColumns: '60px minmax(200px, 2fr) 100px 100px 100px 200px 100px' }}>
                    <div className="linear-cell text-center">Rank</div>
                    <div className="linear-cell">Player</div>
                    <div className="linear-cell text-right">Price</div>
                    <div className="linear-cell text-right">Own%</div>
                    <div className="linear-cell text-center">Form</div>
                    <div className="linear-cell">Explosivity</div>
                    <div className="linear-cell text-right">Haul %</div>
                </div>

                {/* Grid Body */}
                <div>
                    {players.map((player, index) => (
                        <div
                            key={player.id}
                            className="linear-row group"
                            style={{ gridTemplateColumns: '60px minmax(200px, 2fr) 100px 100px 100px 200px 100px' }}
                        >
                            <div className="linear-cell text-center font-bold text-gray-400 group-hover:text-teal-600 tnum">
                                {index + 1}
                            </div>
                            <div className="linear-cell">
                                <div className="flex flex-col">
                                    <span className="font-semibold text-gray-900">{player.web_name}</span>
                                    <span className="text-xs text-gray-500">{player.team} • {getPositionName(player.position)}</span>
                                </div>
                            </div>
                            <div className="linear-cell text-right font-medium text-gray-600 tnum">
                                £{formatPrice(player.price).replace('£', '')}
                            </div>
                            <div className="linear-cell text-right text-gray-500 tnum">
                                {player.ownership}%
                            </div>
                            <div className="linear-cell text-center">
                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium tnum ${player.form_trend === 'improving' ? 'bg-emerald-50 text-emerald-700' :
                                        player.form_trend === 'declining' ? 'bg-red-50 text-red-700' :
                                            'bg-gray-50 text-gray-600'
                                    }`}>
                                    {player.recent_avg_points}
                                </span>
                            </div>
                            <div className="linear-cell">
                                <div className="flex items-center justify-between gap-3">
                                    <span className="text-sm font-bold text-gray-900 tnum">
                                        {player.explosivity_index}
                                    </span>
                                    <div className="w-24 h-1.5 bg-gray-100 rounded-sm overflow-hidden">
                                        <div
                                            className="h-full rounded-sm bg-gradient-to-r from-teal-500 to-emerald-400"
                                            style={{ width: `${player.explosivity_index}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                            <div className="linear-cell text-right font-medium text-gray-600 tnum">
                                {player.haul_probability}%
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default CaptainPicker;
