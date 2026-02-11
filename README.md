# Sports Betting Arbitrage Bot

Automated bot that finds guaranteed profit opportunities across UK bookmakers.

## What This Does

- Scans 20+ bookmakers every 5 minutes
- Finds arbitrage opportunities (guaranteed profit)
- Sends instant Telegram alerts
- Calculates exact stake amounts
- Tracks all bets and profits

## Expected Returns

- **Week 1:** £50-200 (learning phase)
- **Month 1:** £400-800
- **Month 2+:** £800-1,500/month with £1,000 capital

## Quick Setup

### 1. Get API Keys

**Odds API** (for live odds data):
- Sign up at: https://the-odds-api.com/
- Get API key (£20/month recommended)

**Telegram Bot**:
- Open Telegram, search @BotFather
- Send `/newbot` and follow instructions
- Copy the token you receive

### 2. Deploy to Railway

1. Fork this repository
2. Sign up at railway.app
3. Create new project from GitHub repo
4. Add environment variables:
   - `ODDS_API_KEY` = your odds API key
   - `TELEGRAM_BOT_TOKEN` = your telegram bot token
5. Deploy!

### 3. Set Up Bookmaker Accounts

You need accounts at multiple bookmakers:

**Priority 1 (Must Have):**
- Betfair (£200-300 deposit)
- Bet365 (£100)
- William Hill (£100)
- Paddy Power (£100)
- SkyBet (£50-100)

**Priority 2 (Important):**
- Ladbrokes, Coral, BetVictor, Unibet, Betfred (£50 each)

**Priority 3 (Extra):**
- BoyleSports, Betway, Virgin Bet, 888sport, 10Bet (£50 each)

See `SETUP_GUIDE.md` for detailed instructions.

### 4. Start Using

1. Open Telegram and find your bot
2. Send `/start`
3. Bot will scan automatically every 5 minutes
4. When it finds an opportunity, you'll get an alert
5. Place the bets within 2-3 minutes
6. Guaranteed profit!

## Files

- `main.py` - Entry point
- `scanner.py` - Finds arbitrage opportunities
- `telegram_bot.py` - Telegram interface
- `bet_tracker.py` - Tracks bets and profits
- `config.py` - Configuration (don't commit with real keys!)
- `SETUP_GUIDE.md` - Complete setup instructions
- `QUICK_REFERENCE.md` - Quick guide for placing bets
- `BOOKMAKER_TRACKER.md` - Track your accounts

## Environment Variables

Set these in Railway (or .env file locally):

```
ODDS_API_KEY=your_odds_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

## How It Works

1. Bot fetches live odds from multiple bookmakers
2. Calculates if arbitrage exists (prices allow guaranteed profit)
3. Sends Telegram alert with exact stake amounts
4. You place bets on all outcomes
5. No matter which outcome wins, you profit!

**Example:**
- Arsenal vs Chelsea
- Bet £476 on Arsenal @ 2.10 (Bet365)
- Bet £278 on Draw @ 3.60 (William Hill)
- Bet £246 on Chelsea @ 4.20 (William Hill)
- **Total stake: £1,000**
- **Guaranteed return: £1,040-1,050**
- **Profit: £40-50** (no matter who wins!)

## Important Notes

⚠️ **This is NOT gambling** - it's arbitrage (mathematical certainty)

⚠️ **Bookmakers may limit accounts** - expect "gubbing" after 3-6 months

⚠️ **Speed matters** - place bets within 2-3 minutes of alert

⚠️ **UK only** - this is designed for UK bookmakers

✅ **100% legal** in the UK

✅ **Tax-free** - betting winnings aren't taxed in UK

## Support

Read `SETUP_GUIDE.md` for detailed instructions.

For bot issues, check Railway logs.

## License

Personal use only. Do not sell or redistribute.

## Disclaimer

You are responsible for complying with all gambling laws in your jurisdiction. This software is for educational purposes. Use at your own risk.
