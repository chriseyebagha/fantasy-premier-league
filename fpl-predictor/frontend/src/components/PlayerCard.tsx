'use client';

import React, { useState, useEffect } from 'react';
import { BasicPlayer, POSITION_MAP, formatPrice } from '../types/player';

const PlayerCard: React.FC = () => {
  const [players, setPlayers] = useState<BasicPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPosition, setSelectedPosition] = useState<number | null>(null);

  useEffect(() => {
    fetchPlayers();
  }, [selectedPosition]);

  const fetchPlayers = async () => {
    setLoading(true);
    setError(null);

    try {
      const url = selectedPosition
        ? `http://localhost:5001/api/players?position=${selectedPosition}`
        : 'http://localhost:5001/api/players';

      const res = await fetch(url);
      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setPlayers(data);
      }
    } catch (err) {
      setError('Failed to fetch players');
    } finally {
      setLoading(false);
    }
  };

  const getPositionBadgeClass = (pos: number) => {
    switch (pos) {
      case 1: return 'badge-gk';
      case 2: return 'badge-def';
      case 3: return 'badge-mid';
      case 4: return 'badge-fwd';
      default: return '';
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading players...</div>;
  }

  if (error) {
    return <div className="text-center py-12 text-red-600">{error}</div>;
  }

  return (
    <div>
      {/* Position Filter Buttons */}
      <div className="flex gap-2 mb-6">
        <button
          className={`btn ${!selectedPosition ? 'btn-active' : 'btn-secondary'}`}
          onClick={() => setSelectedPosition(null)}
        >
          All
        </button>
        <button
          className={`btn ${selectedPosition === 1 ? 'btn-active' : 'btn-secondary'}`}
          onClick={() => setSelectedPosition(1)}
        >
          GK
        </button>
        <button
          className={`btn ${selectedPosition === 2 ? 'btn-active' : 'btn-secondary'}`}
          onClick={() => setSelectedPosition(2)}
        >
          DEF
        </button>
        <button
          className={`btn ${selectedPosition === 3 ? 'btn-active' : 'btn-secondary'}`}
          onClick={() => setSelectedPosition(3)}
        >
          MID
        </button>
        <button
          className={`btn ${selectedPosition === 4 ? 'btn-active' : 'btn-secondary'}`}
          onClick={() => setSelectedPosition(4)}
        >
          FWD
        </button>
      </div>

      {/* Players Table */}
      <div className="card overflow-x-auto">
        <table>
          <thead>
            <tr>
              <th>Player</th>
              <th>Team</th>
              <th>Position</th>
              <th className="text-center">Predicted Pts</th>
              <th className="text-center">Form</th>
              <th className="text-right">Price</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player) => (
              <tr key={player.id}>
                <td>
                  <div className="font-medium">{player.web_name}</div>
                </td>
                <td className="text-secondary">{player.team}</td>
                <td>
                  <span className={`badge ${getPositionBadgeClass(player.position)}`}>
                    {POSITION_MAP[player.position]}
                  </span>
                </td>
                <td className="text-center font-semibold">{player.predicted_points}</td>
                <td className="text-center">{player.form}</td>
                <td className="text-right font-medium">{formatPrice(player.price)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PlayerCard;
