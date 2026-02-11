"""
Configuration File for Arbitrage Bot
Fill in your API keys and adjust settings here
"""

# =============================================================================
# API CREDENTIALS (You need to get these)
# =============================================================================

# The Odds API - Get free key at: https://the-odds-api.com/
# Free tier: 500 requests/month
# Paid tier: £20/month for 10,000 requests (RECOMMENDED)
ODDS_API_KEY = "YOUR_ODDS_API_KEY_HERE"

# Telegram Bot Token - Get from @BotFather on Telegram
# 1. Open Telegram and search for @BotFather
# 2. Send /newbot
# 3. Follow instructions to create bot
# 4. Copy the token you receive
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

# Your Telegram User ID - Get from @userinfobot on Telegram
# This is who receives the alerts
YOUR_TELEGRAM_USER_ID = 0  # Replace with your actual user ID


# =============================================================================
# ARBITRAGE SETTINGS
# =============================================================================

# Minimum profit percentage to consider (2% = £20 profit on £1000 stake)
MIN_PROFIT_PERCENT = 2.0

# Default stake amount for calculations (in GBP)
DEFAULT_STAKE = 1000

# How often to scan for opportunities (in seconds)
# 300 = 5 minutes (RECOMMENDED to stay within API limits)
SCAN_INTERVAL = 300

# Maximum number of top opportunities to show per scan
MAX_ALERTS_PER_SCAN = 5


# =============================================================================
# BOOKMAKERS TO MONITOR
# =============================================================================

# UK Bookmakers (The bot will find best odds across these)
BOOKMAKERS = [
    'bet365',
    'williamhill',
    'paddypower',
    'betfair',
    'skybet',
    'ladbrokes',
    'coral',
    'betvictor',
    'unibet',
    'betfred',
    'boylesports',
    'betway',
    'virginbet',
    'spreadex',
    'livescorebet'
]


# =============================================================================
# SPORTS TO MONITOR
# =============================================================================

# All available sports
# Remove any you don't want to bet on
SPORTS = [
    'soccer_epl',                    # Premier League
    'soccer_uefa_champs_league',     # Champions League
    'soccer_england_league1',        # League One
    'soccer_england_league2',        # League Two
    'soccer_fa_cup',                 # FA Cup
    'soccer_league_cup',             # League Cup
    'tennis_atp',                    # ATP Tennis
    'tennis_wta',                    # WTA Tennis
    'basketball_nba',                # NBA Basketball
    'cricket_test_match',            # Test Cricket
    'cricket_odi',                   # ODI Cricket
    'americanfootball_nfl',          # NFL
    'icehockey_nhl',                 # NHL
]


# =============================================================================
# RISK MANAGEMENT
# =============================================================================

# Maximum number of simultaneous arbitrage positions
MAX_CONCURRENT_ARBS = 10

# Minimum time before event starts (in hours)
# Don't bet on events starting in less than this time
MIN_TIME_BEFORE_EVENT = 2

# Alert if odds change by more than this percent after alert sent
ODDS_CHANGE_WARNING_THRESHOLD = 5.0


# =============================================================================
# BOOKMAKER ACCOUNT BALANCES (Optional - for tracking)
# =============================================================================

# Update these manually as you deposit/withdraw
# This helps the bot warn you if you don't have enough balance
INITIAL_BALANCES = {
    'bet365': 100,
    'williamhill': 100,
    'paddypower': 100,
    'betfair': 200,  # Main exchange
    'skybet': 50,
    'ladbrokes': 50,
    'coral': 50,
    'betvictor': 50,
    'unibet': 50,
    'betfred': 50,
    'boylesports': 50,
    'betway': 50,
    'virginbet': 50,
    'spreadex': 50,
    'livescorebet': 50
}


# =============================================================================
# ADVANCED SETTINGS (Don't change unless you know what you're doing)
# =============================================================================

# Database file location
DATABASE_PATH = "bets.db"

# Log file location
LOG_FILE = "arbitrage_bot.log"

# Timezone
TIMEZONE = "Europe/London"

# API request timeout (seconds)
API_TIMEOUT = 30

# Number of retries for failed API calls
API_MAX_RETRIES = 3


# =============================================================================
# NOTIFICATION SETTINGS
# =============================================================================

# Send daily summary report
DAILY_REPORT_ENABLED = True
DAILY_REPORT_TIME = "21:00"  # 9 PM

# Alert sound/vibration on Telegram
ENABLE_NOTIFICATIONS = True

# Mute alerts during these hours (24-hour format)
QUIET_HOURS_START = None  # e.g., "23:00" for 11 PM
QUIET_HOURS_END = None    # e.g., "07:00" for 7 AM


# =============================================================================
# VALIDATION
# =============================================================================

def validate_config():
    """Check if configuration is valid"""
    errors = []
    
    if ODDS_API_KEY == "YOUR_ODDS_API_KEY_HERE":
        errors.append("❌ ODDS_API_KEY not set! Get one from https://the-odds-api.com/")
    
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        errors.append("❌ TELEGRAM_BOT_TOKEN not set! Get one from @BotFather on Telegram")
    
    if YOUR_TELEGRAM_USER_ID == 0:
        errors.append("❌ YOUR_TELEGRAM_USER_ID not set! Get it from @userinfobot on Telegram")
    
    if MIN_PROFIT_PERCENT < 1.0:
        errors.append("⚠️  MIN_PROFIT_PERCENT is very low (<1%). You might get too many alerts.")
    
    if DEFAULT_STAKE < 100:
        errors.append("⚠️  DEFAULT_STAKE is very low. Profits will be small.")
    
    if len(BOOKMAKERS) < 5:
        errors.append("⚠️  You're monitoring fewer than 5 bookmakers. Add more for better opportunities.")
    
    if errors:
        print("\n" + "="*60)
        print("CONFIGURATION ERRORS:")
        print("="*60)
        for error in errors:
            print(error)
        print("="*60 + "\n")
        return False
    else:
        print("✅ Configuration is valid!")
        return True


if __name__ == "__main__":
    validate_config()
