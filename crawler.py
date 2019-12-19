#!/usr/bin/env python3

import config
import logging
import QueryExchange
import signal
import sys
import time

if __name__ == "__main__":
    
    # Logging
    logging.basicConfig(filename=f"log/Crawler {time.strftime('%Y-%m-%d %H.%M.%S')}.log", level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    # List of all registered crawlers
    crawlers = []
    
    # Handle SIGINT
    def handle_sigint(sig, frame):
        print("\nGot SIGINT, sending remaining buffer to crawler...")
        for crawler in crawlers:
            crawler.shutdown()
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_sigint)
    
    # Determine start time delay
    if (config.start_time_delay == "immediately"):
        logging.info("Starting crawler.")
        sleep_time_between_exchanges = 5
        
    elif (config.start_time_delay == "slightly_ahead_5_seconds"):
        logging.info("Starting crawler. Waiting for next 4.5 / 9.5 seconds...")
        
        # Current time between 4.5 and 4.999 or 9.5 and 9,999s: Wait for next cycle
        if (time.time() % 5 >= 4.5):
            time.sleep(.51)
        
        time.sleep(4.5 - time.time() % 5)
        sleep_time_between_exchanges = 4.5
    
    elif (config.start_time_delay == "full_5_seconds"):
        logging.info("Starting crawler. Waiting for next full five seconds...")
        time.sleep(5 - time.time() % 5)
        sleep_time_between_exchanges = 5
    
    else:
        raise Exception("Unknown configuration setting for start_time_delay.")
    
    
    
    # Bitstamp
    crawlers.extend([
        QueryExchange.BitstampExchange("bitstamp_usd", "https://www.bitstamp.net/api/v2/order_book/btcusd"),
        QueryExchange.BitstampExchange("bitstamp_eur", "https://www.bitstamp.net/api/v2/order_book/btceur")
    ])
    
    # Current time between 4.5 and 4.999 or 9.5 and 9,999s: Wait for next cycle
    if (sleep_time_between_exchanges == 4.5 and time.time() % 5 >= 4.5):
        time.sleep(.51)
    time.sleep(sleep_time_between_exchanges - time.time() % 5)
    
    
    
    # Bitfinex
    crawlers.extend([
        QueryExchange.BitfinexExchange("bitfinex_usd", "https://api-pub.bitfinex.com/v2/book/tBTCUSD/P0?len=25"),
        QueryExchange.BitfinexExchange("bitfinex_eur", "https://api-pub.bitfinex.com/v2/book/tBTCEUR/P0?len=25")
    ])
    
    # Current time between 4.5 and 4.999 or 9.5 and 9,999s: Wait for next cycle
    if (sleep_time_between_exchanges == 4.5 and time.time() % 5 >= 4.5):
        time.sleep(.51)
    time.sleep(sleep_time_between_exchanges - time.time() % 5)
    
    
    
    
    # Coinbase
    crawlers.extend([
        QueryExchange.CoinbaseExchange("coinbase_usd", "https://api.pro.coinbase.com/products/BTC-USD/book?level=2"),
        QueryExchange.CoinbaseExchange("coinbase_eur", "https://api.pro.coinbase.com/products/BTC-EUR/book?level=2")
    ])
    
    # Current time between 4.5 and 4.999 or 9.5 and 9,999s: Wait for next cycle
    if (sleep_time_between_exchanges == 4.5 and time.time() % 5 >= 4.5):
        time.sleep(.51)
    time.sleep(sleep_time_between_exchanges - time.time() % 5)
    
    
    
    
    # Kraken
    crawlers.append([
        QueryExchange.KrakenExchange("kraken_usd", "https://api.kraken.com/0/public/Depth?pair=XBTUSD&count=10"),
        QueryExchange.KrakenExchange("kraken_eur", "https://api.kraken.com/0/public/Depth?pair=XBTEUR&count=10")
    ])

