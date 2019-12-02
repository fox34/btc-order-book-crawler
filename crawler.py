#!/usr/bin/env python3

# Aggregiere immer 5s des Orderbuches und sende es regelmäßig gesammelt an research.noecho.de

import QueryExchange
import time
import config

if __name__ == "__main__":
    
    # Erzeuge Objekte. Abfrage-Intervall startet automatisch
    if (config.start_time_delay == "immediately"):
        # Starte sofort
        print("Starting crawler.")
        sleep_time_between_exchanges = 5
        
    elif (config.start_time_delay == "slightly_ahead_5_seconds"):
        # Warte etwas weniger als nächste volle fünf Sekunden
        print("Starting crawler. Waiting for next 4.5 / 9.5 seconds...")
        
        # Zwischen 4,5 und 4,999 oder 9,5 und 9,999s: Warte auf nächsten Zyklus
        if (time.time() % 5 >= 4.5):
            time.sleep(.51)
        
        time.sleep(4.5 - time.time() % 5)
        sleep_time_between_exchanges = 4.5
    
    elif (config.start_time_delay == "full_5_seconds"):
        # Warte auf nächste volle fünf Sekunden
        print("Starting crawler. Waiting for next full five seconds...")
        time.sleep(5 - time.time() % 5)
        sleep_time_between_exchanges = 5
    
    else:
        raise Exception("Unknown configuration setting for start_time_delay.")
    
    
    # Bitstamp
    QueryExchange.BitstampExchange("bitstamp_usd", "https://www.bitstamp.net/api/v2/order_book/btcusd")
    QueryExchange.BitstampExchange("bitstamp_eur", "https://www.bitstamp.net/api/v2/order_book/btceur")
    
    
    # Zwischen 4,5 und 4,999 oder 9,5 und 9,999s: Warte auf nächsten Zyklus
    if (sleep_time_between_exchanges == 4.5 and time.time() % 5 >= 4.5):
        time.sleep(.51)
    time.sleep(sleep_time_between_exchanges - time.time() % 5)
    
    # Bitfinex
    # P0 = Aggregation gleicher Preise (Count = Anzahl der Aufträge)
    # R0 = Keine Aggregation der Preise, Rohdaten der Bücher
    # len = Abgefragte Datensätze (1, 25, 100)
    QueryExchange.BitfinexExchange("bitfinex_usd", "https://api-pub.bitfinex.com/v2/book/tBTCUSD/P0?len=25")
    QueryExchange.BitfinexExchange("bitfinex_eur", "https://api-pub.bitfinex.com/v2/book/tBTCEUR/P0?len=25")

    
    # Zwischen 4,5 und 4,999 oder 9,5 und 9,999s: Warte auf nächsten Zyklus
    if (sleep_time_between_exchanges == 4.5 and time.time() % 5 >= 4.5):
        time.sleep(.51)
    time.sleep(sleep_time_between_exchanges - time.time() % 5)
    
    # Coinbase
    # Level = Detailgrad. 1 = Nur bester Bid/Ask; 2 = Top 50 Bid/Ask, aggregiert; 3 = Volles Orderbuch
    QueryExchange.CoinbaseExchange("coinbase_usd", "https://api.pro.coinbase.com/products/BTC-USD/book?level=2")
    QueryExchange.CoinbaseExchange("coinbase_eur", "https://api.pro.coinbase.com/products/BTC-EUR/book?level=2")
    
    
    # Zwischen 4,5 und 4,999 oder 9,5 und 9,999s: Warte auf nächsten Zyklus
    if (sleep_time_between_exchanges == 4.5 and time.time() % 5 >= 4.5):
        time.sleep(.51)
    time.sleep(sleep_time_between_exchanges - time.time() % 5)
    
    # Kraken
    # Count = Maximale Anzahl Bid/Ask
    QueryExchange.KrakenExchange("kraken_usd", "https://api.kraken.com/0/public/Depth?pair=XBTUSD&count=10")
    QueryExchange.KrakenExchange("kraken_eur", "https://api.kraken.com/0/public/Depth?pair=XBTEUR&count=10")
    
