'use client';

import React, { useEffect, useState } from 'react';
import { ExtendedPlayer, formatPrice } from '../types/player';

const PriceTracker: React.FC = () => {
    const [risers, setRisers] = useState<ExtendedPlayer[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchPriceRisers();
    }, []);

    const fetchPriceRisers = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:5001/api/price-risers?top_n=20');
            const data = await res.json();
            setRisers(data);
        } catch (error) {
            console.error('Error fetching price risers:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="space-y-4">
                <div className="skeleton" style={{ height: '60px' }} />
                <div className="skeleton" style={{ height: '400px' }} />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                <div>
                    <h2>Price Rise Tracker</h2>
                    <p className="text-secondary">
                        Players most likely to rise in price based on recent transfer activity
                    </p>
                </div>
                <button onClick={fetchPriceRisers} className="btn btn-secondary">
                    Refresh Data
                </button>
            </div>

            {/* Data Table */}
            <div className="card">
                <table>
                    <thead>
                        <tr>
                            <th>Player</th>
                            <th>Team</th>
                            <th>Position</th>
                            <th className="text-right">Price</th>
                            <th className="text-center">Net Transfers</th>
                            <th className="text-center">Rise Prob</th>
                        </tr>
                    </thead>
                    <tbody>
                        {risers.map((player) => (
                            <tr key={player.id}>
                                <td className="font-medium">{player.web_name}</td>
                                <td className="text-secondary">{player.team}</td>
                                <td>
                                    <span className={`badge ${player.position === 1 ? 'badge-gk' :
                                            player.position === 2 ? 'badge-def' :
                                                player.position === 3 ? 'badge-mid' :
                                                    'badge-fwd'
                                        }`}>
                                        {player.position === 1 ? 'GK' :
                                            player.position === 2 ? 'DEF' :
                                                player.position === 3 ? 'MID' : 'FWD'}
                                    </span>
                                </td>
                                <td className="text-right font-medium">{formatPrice(player.price)}</td>
                                <td className={`text-center font-medium ${player.net_transfers > 0 ? 'text-success' : 'text-danger'}`}>
                                    {player.net_transfers > 0 ? '+' : ''}{(player.net_transfers / 1000).toFixed(1)}k
                                </td>
                                <td className="text-center">
                                    <div style={{
                                        display: 'inline-block',
                                        padding: '0.25rem 0.5rem',
                                        borderRadius: '4px',
                                        backgroundColor: player.price_rise_probability > 75 ? '#dcfce7' : '#f3f4f6',
                                        color: player.price_rise_probability > 75 ? '#166534' : '#374151',
                                        fontWeight: '600',
                                        fontSize: '0.875rem'
                                    }}>
                                        {player.price_rise_probability}%
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default PriceTracker;
