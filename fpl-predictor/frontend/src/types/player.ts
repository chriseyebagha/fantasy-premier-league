// Player type definitions for FPL Predictor

export interface BasicPlayer {
    id: number;
    code: number;
    web_name: string;
    team: string;
    team_id: number;
    position: number;
    price: number;
    form: number;
    xg_90: number;
    xa_90: number;
    difficulty: number;
    predicted_points: number;
    value_score: number;
    status: string;
    chance_of_playing: number | null;
    ownership: number;
    ict_index: number;
}

export interface ExtendedPlayer extends BasicPlayer {
    // Recent form
    recent_avg_points: number;
    recent_minutes: number;
    form_trend: string;

    // Rotation risk
    starting_probability: number;
    min_70_probability: number;
    rotation_risk: string;

    // Captain metrics
    captain_score: number;
    double_digit_hauls: number;

    // Joker metrics
    joker_score: number;
    is_differential: boolean;
    explosivity_index: number;  // NEW: Bayesian explosivity index
    haul_probability: number;    // NEW: Probability of 10+ haul
    hauls_this_season: number;   // NEW: Count of hauls this season

    // Price
    price_rise_probability: number;
    net_transfers: number;

    // Future value
    fixture_run_difficulty: number;
    fixture_run_value: number;
}

export type Player = BasicPlayer | ExtendedPlayer;

export interface Squad {
    formation: string;
    total_cost: number;
    remaining_budget: number;
    starting_11_points: number;
    bench_points: number;
    team_distribution: { [teamName: string]: number };
    position_counts: { [position: string]: number };
    players: {
        starting_11: BasicPlayer[];
        bench: BasicPlayer[];
    };
}

export const POSITION_MAP: { [key: number]: string } = {
    1: 'GK',
    2: 'DEF',
    3: 'MID',
    4: 'FWD',
};

export const POSITION_COLORS: { [key: number]: string } = {
    1: '#8b5cf6', // Purple
    2: '#3b82f6', // Blue
    3: '#10b981', // Green
    4: '#f59e0b', // Amber
};

export const DIFFICULTY_COLORS: { [key: number]: string } = {
    1: '#10b981', // Excellent - green
    2: '#84cc16', // Good - lime
    3: '#f59e0b', // Average - amber
    4: '#f97316', // Hard - orange
    5: '#ef4444', // Very hard - red
};

export const ROTATION_RISK_COLORS = {
    low: '#10b981',
    medium: '#f59e0b',
    high: '#ef4444',
};

export function isExtendedPlayer(player: Player): player is ExtendedPlayer {
    return 'captain_score' in player;
}

export function getDifficultyColor(difficulty: number): string {
    if (difficulty <= 2) return DIFFICULTY_COLORS[2];
    if (difficulty <= 3) return DIFFICULTY_COLORS[3];
    if (difficulty <= 4) return DIFFICULTY_COLORS[4];
    return DIFFICULTY_COLORS[5];
}

export function getRotationRiskColor(risk: 'low' | 'medium' | 'high'): string {
    return ROTATION_RISK_COLORS[risk];
}

export function formatPrice(price: number): string {
    return `£${price.toFixed(1)}m`;
}

export function getFormTrendIcon(trend: 'up' | 'down' | 'stable'): string {
    switch (trend) {
        case 'up':
            return '↗';
        case 'down':
            return '↘';
        default:
            return '→';
    }
}

export function getFormTrendColor(trend: 'up' | 'down' | 'stable'): string {
    switch (trend) {
        case 'up':
            return '#10b981';
        case 'down':
            return '#ef4444';
        default:
            return '#9ca3af';
    }
}
