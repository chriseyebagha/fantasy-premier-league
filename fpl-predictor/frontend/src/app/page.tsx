'use client';

import React, { useState } from 'react';
import PlayerCard from '../components/PlayerCard';
import CaptainPicker from '../components/CaptainPicker';
import PriceTracker from '../components/PriceTracker';

export default function Home() {
    const [activeTab, setActiveTab] = useState<'players' | 'captains' | 'differentials' | 'price-risers'>('players');

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Premium Header */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-emerald-600 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-sm">
                            F
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900 tracking-tight">FPL Predictor</h1>
                            <p className="text-xs text-gray-500 font-medium">AI-Powered Insights</p>
                        </div>
                    </div>
                    <div className="text-xs font-medium text-emerald-600 bg-emerald-50/50 px-3 py-1 rounded-full">
                        Gameweek 13 Active
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Tabs */}
                <div className="tabs">
                    <button
                        className={`tab ${activeTab === 'players' ? 'tab-active' : ''}`}
                        onClick={() => setActiveTab('players')}
                    >
                        Player Explorer
                    </button>
                    <button
                        className={`tab ${activeTab === 'captains' ? 'tab-active' : ''}`}
                        onClick={() => setActiveTab('captains')}
                    >
                        Captains
                    </button>
                    <button
                        className={`tab ${activeTab === 'differentials' ? 'tab-active' : ''}`}
                        onClick={() => setActiveTab('differentials')}
                    >
                        Differentials
                    </button>
                    <button
                        className={`tab ${activeTab === 'price-risers' ? 'tab-active' : ''}`}
                        onClick={() => setActiveTab('price-risers')}
                    >
                        Price Risers
                    </button>
                </div>

                {/* Tab Content */}
                <div className="fade-in min-h-[600px]">
                    {activeTab === 'players' && (
                        <div>
                            <div className="mb-6">
                                <h2 className="text-2xl font-bold text-gray-900 mb-2">Player Explorer</h2>
                                <p className="text-gray-600">Browse and filter players by position with advanced stats</p>
                            </div>
                            <PlayerCard />
                        </div>
                    )}

                    {activeTab === 'captains' && (
                        <CaptainPicker mode="standard" />
                    )}

                    {activeTab === 'differentials' && (
                        <CaptainPicker mode="joker" />
                    )}

                    {activeTab === 'price-risers' && (
                        <div>
                            <div className="mb-6">
                                <h2 className="text-2xl font-bold text-gray-900 mb-2">Price Rise Predictions</h2>
                                <p className="text-gray-600">Players likely to increase in price based on transfer trends</p>
                            </div>
                            <PriceTracker />
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
