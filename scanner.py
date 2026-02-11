"""
Sports Betting Arbitrage Scanner
Monitors 20+ bookmakers for guaranteed profit opportunities
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArbitrageScanner:
    """Main scanner that finds arbitrage opportunities across bookmakers"""
    
    def __init__(self, api_key: str, min_profit_percent: float = 2.0):
        self.api_key = api_key
        self.min_profit_percent = min_profit_percent
        self.base_url = "https://api.the-odds-api.com/v4"
        
        # UK Bookmakers to monitor
        self.bookmakers = [
            'bet365', 'williamhill', 'paddypower', 'betfair', 'skybet',
            'ladbrokes', 'coral', 'betvictor', 'unibet', 'betfred',
            'boylesports', 'betway', 'virginbet', 'spreadex', 'livescorebet'
        ]
        
        # Sports to monitor (all major UK markets)
        self.sports = [
            'soccer_epl',              # Premier League
            'soccer_uefa_champs_league', # Champions League
            'soccer_england_league1',   # League One
            'soccer_england_league2',   # League Two
            'tennis_atp',              # ATP Tennis
            'tennis_wta',              # WTA Tennis
            'basketball_nba',          # NBA
            'cricket_test_match',      # Cricket
            'americanfootball_nfl',    # NFL
            'icehockey_nhl'            # NHL
        ]
        
    async def fetch_odds(self, sport: str) -> Optional[List[Dict]]:
        """Fetch current odds for a specific sport"""
        url = f"{self.base_url}/sports/{sport}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': 'uk',
            'markets': 'h2h',  # Head to head (match winner)
            'oddsFormat': 'decimal',
            'bookmakers': ','.join(self.bookmakers)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"API error for {sport}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching odds for {sport}: {e}")
            return None
    
    def calculate_arbitrage(self, odds_data: List[Dict]) -> List[Dict]:
        """
        Calculate arbitrage opportunities from odds data
        
        Returns list of profitable arbitrage opportunities
        """
        opportunities = []
        
        for event in odds_data:
            if not event.get('bookmakers'):
                continue
                
            event_name = f"{event['home_team']} vs {event['away_team']}"
            sport = event.get('sport_title', 'Unknown')
            commence_time = event.get('commence_time', '')
            
            # Extract all odds for this event
            all_odds = {}
            for bookmaker in event['bookmakers']:
                bookie_name = bookmaker['key']
                markets = bookmaker.get('markets', [])
                
                for market in markets:
                    if market['key'] != 'h2h':
                        continue
                        
                    outcomes = market.get('outcomes', [])
                    for outcome in outcomes:
                        outcome_name = outcome['name']
                        price = outcome['price']
                        
                        # Store best odds for each outcome
                        if outcome_name not in all_odds:
                            all_odds[outcome_name] = {'price': price, 'bookmaker': bookie_name}
                        elif price > all_odds[outcome_name]['price']:
                            all_odds[outcome_name] = {'price': price, 'bookmaker': bookie_name}
            
            # Check if we have odds for all outcomes
            if len(all_odds) < 2:
                continue
            
            # Calculate if arbitrage exists
            inverse_sum = sum(1.0 / odds['price'] for odds in all_odds.values())
            
            # If inverse sum < 1.0, we have an arbitrage opportunity
            if inverse_sum < 1.0:
                profit_percent = ((1.0 / inverse_sum) - 1.0) * 100
                
                # Only include if profit meets minimum threshold
                if profit_percent >= self.min_profit_percent:
                    opportunities.append({
                        'event': event_name,
                        'sport': sport,
                        'commence_time': commence_time,
                        'profit_percent': round(profit_percent, 2),
                        'outcomes': all_odds,
                        'timestamp': datetime.now().isoformat()
                    })
        
        return opportunities
    
    def calculate_stakes(self, total_stake: float, outcomes: Dict) -> Dict:
        """
        Calculate exact stake amounts for each outcome to guarantee profit
        
        Args:
            total_stake: Total amount to invest (e.g., £1000)
            outcomes: Dict of outcomes with their best odds
        
        Returns:
            Dict with stake amounts for each outcome
        """
        inverse_sum = sum(1.0 / outcome['price'] for outcome in outcomes.values())
        
        stakes = {}
        for outcome_name, odds_data in outcomes.items():
            # Calculate proportional stake
            stake = (total_stake / odds_data['price']) / inverse_sum
            stakes[outcome_name] = {
                'stake': round(stake, 2),
                'bookmaker': odds_data['bookmaker'],
                'odds': odds_data['price'],
                'potential_return': round(stake * odds_data['price'], 2)
            }
        
        return stakes
    
    async def scan_all_sports(self) -> List[Dict]:
        """Scan all configured sports for arbitrage opportunities"""
        logger.info(f"Scanning {len(self.sports)} sports for arbitrage...")
        
        all_opportunities = []
        
        for sport in self.sports:
            logger.info(f"Fetching odds for {sport}...")
            odds_data = await self.fetch_odds(sport)
            
            if odds_data:
                opportunities = self.calculate_arbitrage(odds_data)
                if opportunities:
                    logger.info(f"Found {len(opportunities)} arbitrage opportunities in {sport}")
                    all_opportunities.extend(opportunities)
            
            # Respect API rate limits
            await asyncio.sleep(1)
        
        # Sort by profit percentage (highest first)
        all_opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)
        
        return all_opportunities
    
    async def continuous_scan(self, interval_seconds: int = 300):
        """
        Continuously scan for opportunities at specified interval
        
        Args:
            interval_seconds: Time between scans (default 5 minutes)
        """
        logger.info(f"Starting continuous scan (every {interval_seconds} seconds)...")
        
        while True:
            try:
                opportunities = await self.scan_all_sports()
                
                if opportunities:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"FOUND {len(opportunities)} ARBITRAGE OPPORTUNITIES")
                    logger.info(f"{'='*60}\n")
                    
                    for opp in opportunities[:5]:  # Show top 5
                        logger.info(f"Event: {opp['event']}")
                        logger.info(f"Sport: {opp['sport']}")
                        logger.info(f"Profit: {opp['profit_percent']}%")
                        logger.info(f"Outcomes: {len(opp['outcomes'])}")
                        logger.info("-" * 60)
                else:
                    logger.info("No arbitrage opportunities found in this scan.")
                
                # Wait before next scan
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in continuous scan: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying


# Example usage
async def main():
    # Replace with your actual API key from the-odds-api.com
    API_KEY = "YOUR_API_KEY_HERE"
    
    # Create scanner with 2% minimum profit threshold
    scanner = ArbitrageScanner(api_key=API_KEY, min_profit_percent=2.0)
    
    # Run a single scan
    print("Running single scan...")
    opportunities = await scanner.scan_all_sports()
    
    if opportunities:
        print(f"\nFound {len(opportunities)} opportunities!\n")
        
        for opp in opportunities:
            print(f"{'='*80}")
            print(f"EVENT: {opp['event']}")
            print(f"SPORT: {opp['sport']}")
            print(f"PROFIT: {opp['profit_percent']}%")
            print(f"START TIME: {opp['commence_time']}")
            print(f"\nOUTCOMES:")
            
            # Calculate stakes for £1000 total investment
            stakes = scanner.calculate_stakes(1000, opp['outcomes'])
            
            for outcome, stake_data in stakes.items():
                print(f"  {outcome}:")
                print(f"    Stake: £{stake_data['stake']}")
                print(f"    Bookmaker: {stake_data['bookmaker']}")
                print(f"    Odds: {stake_data['odds']}")
                print(f"    Return: £{stake_data['potential_return']}")
            
            print(f"\nGuaranteed profit: £{round(list(stakes.values())[0]['potential_return'] - 1000, 2)}")
            print(f"{'='*80}\n")
    else:
        print("No arbitrage opportunities found.")


if __name__ == "__main__":
    asyncio.run(main())
