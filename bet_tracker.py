"""
Bet Tracker - Records all arbitrage bets and calculates P&L
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
import sqlite3


class BetTracker:
    """Track all arbitrage bets and calculate profits"""
    
    def __init__(self, db_path: str = "bets.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create arbitrage opportunities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                sport TEXT NOT NULL,
                commence_time TEXT,
                profit_percent REAL,
                total_stake REAL,
                guaranteed_profit REAL,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Create individual bets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER,
                outcome TEXT NOT NULL,
                bookmaker TEXT NOT NULL,
                odds REAL NOT NULL,
                stake REAL NOT NULL,
                potential_return REAL NOT NULL,
                placed_at TEXT,
                settled_at TEXT,
                result TEXT,
                actual_return REAL,
                FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
            )
        """)
        
        # Create bookmaker balances table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balances (
                bookmaker TEXT PRIMARY KEY,
                balance REAL NOT NULL,
                last_updated TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_opportunity(self, opportunity: Dict, stakes: Dict, total_stake: float) -> int:
        """
        Log a new arbitrage opportunity
        
        Returns the opportunity ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate guaranteed profit
        first_return = list(stakes.values())[0]['potential_return']
        guaranteed_profit = first_return - total_stake
        
        # Insert opportunity
        cursor.execute("""
            INSERT INTO opportunities (
                event, sport, commence_time, profit_percent, 
                total_stake, guaranteed_profit, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            opportunity['event'],
            opportunity['sport'],
            opportunity.get('commence_time', ''),
            opportunity['profit_percent'],
            total_stake,
            guaranteed_profit,
            datetime.now().isoformat()
        ))
        
        opportunity_id = cursor.lastrowid
        
        # Insert individual bets
        for outcome, stake_data in stakes.items():
            cursor.execute("""
                INSERT INTO bets (
                    opportunity_id, outcome, bookmaker, odds, 
                    stake, potential_return
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                opportunity_id,
                outcome,
                stake_data['bookmaker'],
                stake_data['odds'],
                stake_data['stake'],
                stake_data['potential_return']
            ))
        
        conn.commit()
        conn.close()
        
        return opportunity_id
    
    def mark_bets_placed(self, opportunity_id: int):
        """Mark that bets for this opportunity have been placed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bets 
            SET placed_at = ? 
            WHERE opportunity_id = ?
        """, (datetime.now().isoformat(), opportunity_id))
        
        cursor.execute("""
            UPDATE opportunities 
            SET status = 'placed' 
            WHERE id = ?
        """, (opportunity_id,))
        
        conn.commit()
        conn.close()
    
    def settle_bet(self, bet_id: int, won: bool, actual_return: float = 0):
        """
        Settle an individual bet
        
        Args:
            bet_id: ID of the bet
            won: Whether this bet won
            actual_return: Actual return received (if won)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bets 
            SET settled_at = ?, 
                result = ?, 
                actual_return = ?
            WHERE id = ?
        """, (
            datetime.now().isoformat(),
            'won' if won else 'lost',
            actual_return if won else 0,
            bet_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_pending_opportunities(self) -> List[Dict]:
        """Get all pending opportunities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM opportunities 
            WHERE status = 'pending' 
            ORDER BY timestamp DESC
        """)
        
        opportunities = []
        for row in cursor.fetchall():
            opportunities.append({
                'id': row[0],
                'event': row[1],
                'sport': row[2],
                'profit_percent': row[4],
                'guaranteed_profit': row[6]
            })
        
        conn.close()
        return opportunities
    
    def get_stats(self, period: str = 'all') -> Dict:
        """
        Calculate statistics
        
        Args:
            period: 'day', 'week', 'month', or 'all'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build time filter
        time_filter = ""
        if period == 'day':
            time_filter = "WHERE timestamp > datetime('now', '-1 day')"
        elif period == 'week':
            time_filter = "WHERE timestamp > datetime('now', '-7 days')"
        elif period == 'month':
            time_filter = "WHERE timestamp > datetime('now', '-30 days')"
        
        # Get total opportunities
        cursor.execute(f"SELECT COUNT(*) FROM opportunities {time_filter}")
        total_opportunities = cursor.fetchone()[0]
        
        # Get placed bets
        cursor.execute(f"""
            SELECT COUNT(*) FROM opportunities 
            {time_filter.replace('WHERE', 'AND') if time_filter else 'WHERE status = "placed"'}
            {'AND' if time_filter else 'WHERE'} status = 'placed'
        """)
        placed_count = cursor.fetchone()[0]
        
        # Get total guaranteed profit from placed bets
        cursor.execute(f"""
            SELECT SUM(guaranteed_profit) FROM opportunities 
            {time_filter.replace('WHERE', 'AND') if time_filter else 'WHERE status = "placed"'}
            {'AND' if time_filter else 'WHERE'} status = 'placed'
        """)
        total_profit = cursor.fetchone()[0] or 0
        
        # Get average profit percent
        cursor.execute(f"""
            SELECT AVG(profit_percent) FROM opportunities 
            {time_filter.replace('WHERE', 'AND') if time_filter else 'WHERE status = "placed"'}
            {'AND' if time_filter else 'WHERE'} status = 'placed'
        """)
        avg_profit_pct = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_opportunities': total_opportunities,
            'bets_placed': placed_count,
            'total_profit': round(total_profit, 2),
            'average_roi': round(avg_profit_pct, 2),
            'period': period
        }
    
    def update_bookmaker_balance(self, bookmaker: str, balance: float):
        """Update the balance for a bookmaker"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO balances (bookmaker, balance, last_updated)
            VALUES (?, ?, ?)
        """, (bookmaker, balance, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_all_balances(self) -> Dict[str, float]:
        """Get current balances across all bookmakers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT bookmaker, balance FROM balances")
        balances = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return balances
    
    def generate_daily_report(self) -> str:
        """Generate a daily performance report"""
        stats = self.get_stats('day')
        week_stats = self.get_stats('week')
        
        report = f"""
📊 **DAILY ARBITRAGE REPORT**
Date: {datetime.now().strftime('%Y-%m-%d')}

**Today:**
🎯 Opportunities Found: {stats['total_opportunities']}
✅ Bets Placed: {stats['bets_placed']}
💰 Total Profit: £{stats['total_profit']}
📈 Average ROI: {stats['average_roi']}%

**This Week:**
💰 Total Profit: £{week_stats['total_profit']}
📊 Bets Placed: {week_stats['bets_placed']}

**Account Balances:**
"""
        
        balances = self.get_all_balances()
        total_balance = sum(balances.values())
        
        for bookmaker, balance in sorted(balances.items(), key=lambda x: x[1], reverse=True):
            report += f"\n{bookmaker.upper()}: £{balance}"
        
        report += f"\n\n💵 **Total Across All Bookies: £{total_balance}**"
        
        return report
    
    def export_to_csv(self, filepath: str, period: str = 'all'):
        """Export bet history to CSV for analysis"""
        import csv
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        time_filter = ""
        if period == 'month':
            time_filter = "WHERE o.timestamp > datetime('now', '-30 days')"
        
        cursor.execute(f"""
            SELECT 
                o.event,
                o.sport,
                o.commence_time,
                o.profit_percent,
                o.guaranteed_profit,
                b.outcome,
                b.bookmaker,
                b.odds,
                b.stake,
                b.placed_at,
                b.result
            FROM opportunities o
            JOIN bets b ON o.id = b.opportunity_id
            {time_filter}
            ORDER BY o.timestamp DESC
        """)
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Event', 'Sport', 'Start Time', 'Profit %', 'Guaranteed Profit',
                'Outcome', 'Bookmaker', 'Odds', 'Stake', 'Placed At', 'Result'
            ])
            writer.writerows(cursor.fetchall())
        
        conn.close()
        print(f"Exported bet history to {filepath}")


# Example usage
if __name__ == "__main__":
    tracker = BetTracker()
    
    # Example: Log an opportunity
    opportunity = {
        'event': 'Arsenal vs Chelsea',
        'sport': 'Premier League',
        'commence_time': '2026-02-15T15:00:00',
        'profit_percent': 4.2
    }
    
    stakes = {
        'Arsenal': {'bookmaker': 'bet365', 'odds': 2.1, 'stake': 476, 'potential_return': 1000},
        'Draw': {'bookmaker': 'williamhill', 'odds': 3.6, 'stake': 278, 'potential_return': 1001},
        'Chelsea': {'bookmaker': 'williamhill', 'odds': 4.2, 'stake': 246, 'potential_return': 1033}
    }
    
    opp_id = tracker.log_opportunity(opportunity, stakes, 1000)
    print(f"Logged opportunity with ID: {opp_id}")
    
    # Mark as placed
    tracker.mark_bets_placed(opp_id)
    
    # Get stats
    stats = tracker.get_stats('day')
    print(f"\nToday's Stats: {stats}")
    
    # Generate report
    print("\n" + tracker.generate_daily_report())
