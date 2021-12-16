# WARNING: This repository is not maintained any longer.

# Periodically crawl order books of common bitcoin exchanges

## Data description

Request order books in short intervals. Periodically send aggregated data to
custom api endpoint for aggregation in .csv/MySQL/whatever.

### Bitstamp

- Reference: https://www.bitstamp.net/api/
- API URLs:
    - https://www.bitstamp.net/api/v2/order_book/btcusd
    - https://www.bitstamp.net/api/v2/order_book/btceur
- Request interval: 5 seconds

### Bitfinex

- Reference: https://docs.bitfinex.com/reference#rest-public-books
- API URLs:
    - https://api-pub.bitfinex.com/v2/book/tBTCUSD/P0?len=25
    - https://api-pub.bitfinex.com/v2/book/tBTCEUR/P0?len=25
- Request interval: 5 seconds

### Coinbase

- Reference: https://docs.pro.coinbase.com/#get-product-order-book
- API URLs:
    - https://api.pro.coinbase.com/products/BTC-USD/book?level=2
    - https://api.pro.coinbase.com/products/BTC-EUR/book?level=2
- Request interval: 5 seconds

### ~Kraken~

Kraken will be queried, however, the crawling process fails after a while because of API limitations.

- Reference: https://www.kraken.com/features/api#get-order-book
- API URLs:
    - https://api.kraken.com/0/public/Depth?pair=XBTUSD&count=10
    - https://api.kraken.com/0/public/Depth?pair=XBTEUR&count=10
- Request interval: 5 seconds
