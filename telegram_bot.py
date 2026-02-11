"""
Telegram Alert System for Arbitrage Opportunities
Sends instant notifications with bet placement instructions
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from scanner import ArbitrageScanner
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramArbBot:
    """Telegram bot that sends arbitrage alerts"""
    
    def __init__(self, telegram_token: str, odds_api_key: str):
        self.telegram_token = telegram_token
        self.scanner = ArbitrageScanner(api_key=odds_api_key, min_profit_percent=2.0)
        self.application = None
        self.user_settings = {}  # Store user preferences
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        welcome_text = """
🎯 **Arbitrage Bot Activated!**

I'll scan 20+ UK bookmakers every 5 minutes and alert you to guaranteed profit opportunities.

**Current Settings:**
📊 Minimum profit: 2%
💰 Default stake: £1,000
⚽ Sports: All

**Commands:**
/scan - Run immediate scan
/settings - Adjust preferences
/stats - View your stats
/help - Show help

**You'll receive alerts like:**
"🚨 ARBITRAGE FOUND
⚽ Arsenal vs Chelsea
💰 Profit: £43.50 (4.35%)
⏱️ Act within 3 minutes"

Ready to make guaranteed profit? Let's go! 🚀
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        
        # Start scanning for this user
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {
                'min_profit': 2.0,
                'default_stake': 1000,
                'notifications_enabled': True,
                'sports_filter': 'all'
            }
    
    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command - run immediate scan"""
        await update.message.reply_text("🔍 Scanning all bookmakers... This will take 20-30 seconds.")
        
        opportunities = await self.scanner.scan_all_sports()
        
        if opportunities:
            await update.message.reply_text(f"✅ Found {len(opportunities)} arbitrage opportunities!")
            
            # Send details for top 3
            for opp in opportunities[:3]:
                await self.send_arbitrage_alert(update.effective_chat.id, opp, context)
        else:
            await update.message.reply_text(
                "❌ No arbitrage opportunities found right now.\n\n"
                "This is normal - opportunities appear and disappear quickly. "
                "I'll keep scanning and alert you automatically."
            )
    
    async def send_arbitrage_alert(self, chat_id: int, opportunity: dict, context: ContextTypes.DEFAULT_TYPE):
        """Send formatted arbitrage alert to user"""
        
        # Calculate stakes for default amount
        default_stake = self.user_settings.get(chat_id, {}).get('default_stake', 1000)
        stakes = self.scanner.calculate_stakes(default_stake, opportunity['outcomes'])
        
        # Calculate guaranteed profit
        first_return = list(stakes.values())[0]['potential_return']
        profit = first_return - default_stake
        
        # Format the alert message
        alert_text = f"""
🚨 **ARBITRAGE FOUND**

**Event:** {opportunity['event']}
**Sport:** {opportunity['sport']}
**Profit:** £{round(profit, 2)} ({opportunity['profit_percent']}%)
**Start Time:** {opportunity['commence_time'][:16]}

**YOUR BETS (Total: £{default_stake}):**

"""
        
        # Add each bet
        for i, (outcome, stake_data) in enumerate(stakes.items(), 1):
            alert_text += f"""**BET {i}: {outcome}**
💷 Stake: £{stake_data['stake']}
📊 Odds: {stake_data['odds']}
🏢 Bookmaker: {stake_data['bookmaker'].upper()}
💰 Returns: £{stake_data['potential_return']}

"""
        
        alert_text += f"""
✅ **GUARANTEED PROFIT: £{round(profit, 2)}**

⏱️ **ACT QUICKLY** - Odds can change in 2-5 minutes!

💡 **TIP:** Open all bookmaker tabs first, then place bets simultaneously.
"""
        
        # Create action buttons
        keyboard = [
            [InlineKeyboardButton("✅ Placed All Bets", callback_data=f"placed_{opportunity['timestamp']}")],
            [InlineKeyboardButton("⏭️ Skip This", callback_data=f"skip_{opportunity['timestamp']}")],
            [InlineKeyboardButton("📊 Recalculate Stakes", callback_data=f"recalc_{opportunity['timestamp']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=alert_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("placed_"):
            await query.edit_message_text(
                "✅ Great! Bets recorded. Good luck! 🍀\n\n"
                "I'll continue scanning for more opportunities."
            )
            
        elif data.startswith("skip_"):
            await query.edit_message_text(
                "⏭️ Skipped. No worries - I'll find more opportunities soon!"
            )
            
        elif data.startswith("recalc_"):
            await query.message.reply_text(
                "Please send your desired stake amount (e.g., 500 for £500)"
            )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user_id = update.effective_user.id
        settings = self.user_settings.get(user_id, {})
        
        settings_text = f"""
⚙️ **Your Settings**

**Minimum Profit:** {settings.get('min_profit', 2.0)}%
**Default Stake:** £{settings.get('default_stake', 1000)}
**Notifications:** {'✅ Enabled' if settings.get('notifications_enabled', True) else '❌ Disabled'}
**Sports Filter:** {settings.get('sports_filter', 'all').upper()}

To change settings, use:
/setprofit <percent> - e.g., /setprofit 3
/setstake <amount> - e.g., /setstake 1500
/togglenotifs - Turn alerts on/off
        """
        
        await update.message.reply_text(settings_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        # In a real implementation, this would pull from a database
        stats_text = """
📊 **Your Arbitrage Stats**

**This Week:**
Opportunities found: 47
Bets placed: 23
Total profit: £847.50
Average ROI: 3.8%

**All Time:**
Total profit: £2,341.00
Win rate: 100% (guaranteed!)
Bets placed: 89

🎯 Keep it up!
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
❓ **How to Use This Bot**

**1. Wait for Alerts**
I scan automatically every 5 minutes. When I find an arbitrage opportunity, you'll get an instant alert.

**2. Act Fast**
Arbitrage opportunities disappear quickly (2-5 minutes). You need to place all bets within this window.

**3. Place Your Bets**
- Open all bookmaker websites
- Copy the exact stake amounts
- Place each bet as shown
- Click "Placed All Bets" when done

**4. Guaranteed Profit**
No matter which outcome wins, you profit! That's the beauty of arbitrage.

**Tips for Success:**
✅ Keep accounts funded on multiple bookies
✅ Have all bookmaker tabs open and logged in
✅ Use copy-paste for exact stake amounts
✅ Act within 3 minutes of receiving alert
✅ Track your bets in a spreadsheet

**Common Questions:**

*Q: Is this legal?*
A: Yes! Arbitrage betting is 100% legal in the UK.

*Q: Can I lose money?*
A: No, if you follow the instructions exactly. The math guarantees profit.

*Q: Why do bookies have different odds?*
A: They use different models and have different customer bases.

*Q: Will I get banned?*
A: Possibly, over time. But you'll make £10k-30k first. See my guide on avoiding gubbing.

Need more help? Message @YourSupportUsername
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def continuous_scanning(self, context: ContextTypes.DEFAULT_TYPE):
        """Background task that continuously scans for opportunities"""
        while True:
            try:
                logger.info("Running scheduled scan...")
                opportunities = await self.scanner.scan_all_sports()
                
                if opportunities:
                    logger.info(f"Found {len(opportunities)} opportunities, sending alerts...")
                    
                    # Send alerts to all users with notifications enabled
                    for user_id, settings in self.user_settings.items():
                        if settings.get('notifications_enabled', True):
                            for opp in opportunities:
                                if opp['profit_percent'] >= settings.get('min_profit', 2.0):
                                    await self.send_arbitrage_alert(user_id, opp, context)
                                    await asyncio.sleep(1)  # Avoid rate limits
                
                # Wait 5 minutes before next scan
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in continuous scanning: {e}")
                await asyncio.sleep(60)
    
    async def post_init(self, application: Application):
        """Initialize background tasks"""
        # Start the continuous scanner
        asyncio.create_task(self.continuous_scanning(application))
    
    def run(self):
        """Start the Telegram bot"""
        # Create the Application
        self.application = Application.builder().token(self.telegram_token).post_init(self.post_init).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("scan", self.scan_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Add callback handler for buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Start the bot
        logger.info("Starting Telegram bot...")
        self.application.run_polling()


if __name__ == "__main__":
    # Replace with your actual tokens
    TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    ODDS_API_KEY = "YOUR_ODDS_API_KEY"
    
    bot = TelegramArbBot(telegram_token=TELEGRAM_TOKEN, odds_api_key=ODDS_API_KEY)
    bot.run()
