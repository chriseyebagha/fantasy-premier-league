// Official FPL 2024/25 Abbreviations
export const TEAM_ABBREVIATIONS: Record<string, string> = {
    'Arsenal': 'ARS',
    'Aston Villa': 'AVL',
    'Bournemouth': 'BOU',
    'Brentford': 'BRE',
    'Brighton': 'BHA',
    'Brighton & Hove Albion': 'BHA',
    'Burnley': 'BUR', // Kept for legacy/data consistency
    'Chelsea': 'CHE',
    'Crystal Palace': 'CRY',
    'Everton': 'EVE',
    'Fulham': 'FUL',
    'Ipswich': 'IPS',
    'Ipswich Town': 'IPS',
    'Leicester': 'LEI',
    'Leicester City': 'LEI',
    'Liverpool': 'LIV',
    'Luton': 'LUT', // Kept for legacy/data consistency
    'Luton Town': 'LUT',
    'Man City': 'MCI',
    'Manchester City': 'MCI',
    'Man Utd': 'MUN',
    'Manchester United': 'MUN',
    'Newcastle': 'NEW',
    'Newcastle United': 'NEW',
    'Nott\'m Forest': 'NFO',
    'Nottingham Forest': 'NFO',
    'Sheffield Utd': 'SHU', // Kept for legacy/data consistency
    'Sheffield United': 'SHU',
    'Southampton': 'SOU',
    'Spurs': 'TOT',
    'Tottenham': 'TOT',
    'Tottenham Hotspur': 'TOT',
    'West Ham': 'WHU',
    'West Ham United': 'WHU',
    'Wolves': 'WOL',
    'Wolverhampton': 'WOL',
    'Wolverhampton Wanderers': 'WOL',

    // Robust Mappings for non-standard/feed-specific inputs
    'AST': 'AVL', // Fix for "AST" input
    'MNC': 'MCI',
    'MNU': 'MUN',
    'NOT': 'NFO', // Fix for potential "NOT" input
    'NFO': 'NFO', // Self-map to be safe
    'SHU': 'SHU',
    'SOU': 'SOU',
};

// Also support reverse mapping if needed or just standard 3-letter codes
// Usually FPL fixtures come as "LIV(A)" or "MCI(H)"
// Or maybe "Liverpool" if the backend expands it.
// We will function defensively.

export const formatFixture = (fixture: string | undefined): string => {
    if (!fixture) return '';

    // If it's empty
    if (fixture.trim() === '') return '';

    // CHECK 1: Is it in format "Team (H)" or "Team (A)"?
    // Regex: Match Name (Group 1) and Home/Away (Group 2)
    const match = fixture.match(/^(.+?)\s?(\([HA]\))$/i);

    let teamRaw = fixture;
    let suffix = '';

    if (match) {
        teamRaw = match[1].trim(); // e.g. "Man City" or "MCI"
        suffix = match[2].toUpperCase(); // e.g. "(H)"
    } else {
        // Maybe just "Man City" without (H)/(A)
        teamRaw = fixture.trim();
    }

    // Try to map teamRaw to standard abbreviation
    // If it's already a 3 letter code, keep it (e.g. MCI)
    // If it's a full name in our map (e.g. Man City), map it.
    let teamAbbr = teamRaw;
    if (TEAM_ABBREVIATIONS[teamRaw]) {
        teamAbbr = TEAM_ABBREVIATIONS[teamRaw];
    } else if (teamRaw.toUpperCase() in Object.values(TEAM_ABBREVIATIONS)) {
        // It's already an abbreviation (values check is rough without a reverse map but mostly safe for 3 chars)
        teamAbbr = teamRaw.toUpperCase();
    } else {
        // Try uppercase just in case
        const upper = teamRaw.toUpperCase();
        // If it's 3 letters, assume it's good
        if (upper.length === 3) teamAbbr = upper;
        // Else check map again
        else if (TEAM_ABBREVIATIONS[teamRaw]) teamAbbr = TEAM_ABBREVIATIONS[teamRaw];
    }

    // Handle "vs"
    // "vs" implies "against".
    // We want "vs MCI (H)" or "vs MCI"
    // Ensure space between vs and team: "vs "
    return `vs ${teamAbbr} ${suffix}`.trim();
};

export const getPositionText = (elementType: number): string => {
    switch (elementType) {
        case 1: return 'GK';
        case 2: return 'DEF';
        case 3: return 'MID';
        case 4: return 'FWD';
        default: return '';
    }
};
