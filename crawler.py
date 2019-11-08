#!/usr/bin/env python3

# Aggregiere immer 5s des Orderbuches und sende es regelmäßig gesammelt an research.noecho.de

import QueryExchange
from time import sleep

if __name__ == "__main__":
    
    # Erzeuge Objekte, Infinite Loop-Timer startet automatisch
    # Bitstamp
    QueryExchange.BitstampExchange("bitstamp_usd", "https://www.bitstamp.net/api/v2/order_book/btcusd")
    QueryExchange.BitstampExchange("bitstamp_eur", "https://www.bitstamp.net/api/v2/order_book/btceur")
    sleep(1)
    
    # Bitfinex
    # P0 = Aggregation gleicher Preise (Count = Anzahl der Aufträge)
    # R0 = Keine Aggregation der Preise, Rohdaten der Bücher
    # len = Abgefragte Datensätze (1, 25, 100)
    QueryExchange.BitfinexExchange("bitfinex_usd", "https://api-pub.bitfinex.com/v2/book/tBTCUSD/P0?len=25")
    QueryExchange.BitfinexExchange("bitfinex_eur", "https://api-pub.bitfinex.com/v2/book/tBTCEUR/P0?len=25")
    sleep(1)
    
    # Coinbase
    # Level = Detailgrad. 1 = Nur bester Bid/Ask; 2 = Top 50 Bid/Ask, aggregiert; 3 = Volles Orderbuch
    QueryExchange.CoinbaseExchange("coinbase_usd", "https://api.pro.coinbase.com/products/BTC-USD/book?level=2")
    QueryExchange.CoinbaseExchange("coinbase_eur", "https://api.pro.coinbase.com/products/BTC-EUR/book?level=2")  
    
