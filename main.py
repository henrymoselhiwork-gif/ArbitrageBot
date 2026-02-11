#!/usr/bin/env python3
"""
Main entry point for the Arbitrage Bot
This file is what Railway will execute
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    
    # Check if required environment variables are set
    required_vars = ['ODDS_API_KEY', 'TELEGRAM_BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these in Railway's environment variables settings")
        sys.exit(1)
    
    # Import and run the bot
    try:
        from telegram_bot import TelegramArbBot
        
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        odds_api_key = os.getenv('ODDS_API_KEY')
        
        logger.info("Starting Arbitrage Bot...")
        logger.info("Bot will scan for opportunities every 5 minutes")
        
        bot = TelegramArbBot(telegram_token=telegram_token, odds_api_key=odds_api_key)
        bot.run()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
