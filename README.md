# Auftragsbücher für verschiedene Börsen regelmäßig abfragen

## Datenbeschreibung

Abfrage erfolgt in kurzen Abständen.
Nach je fünf Minuten werden die Daten aggregiert auf einem eigenen Server in der zugehörigen .csv gespeichert.
Mehrere Aufträge mit dem selben Preislimit werden automatisch (durch die Börsen) aggregiert.


### Bitstamp

- Referenz: https://www.bitstamp.net/api/
- Abfrage folgender URLs:
    - https://www.bitstamp.net/api/v2/order_book/btcusd
    - https://www.bitstamp.net/api/v2/order_book/btceur
- Abfrageintervall: 5 Sekunden

### Bitfinex

- Referenz: https://docs.bitfinex.com/reference#rest-public-books
- Abfrage folgender URLs:
    - https://api-pub.bitfinex.com/v2/book/tBTCUSD/P0?len=25
    - https://api-pub.bitfinex.com/v2/book/tBTCEUR/P0?len=25
- Abfrageintervall: 5 Sekunden

### Coinbase

- Referenz: https://docs.pro.coinbase.com/#get-product-order-book
- Abfrage folgender URLs:
    - https://api.pro.coinbase.com/products/BTC-USD/book?level=2
    - https://api.pro.coinbase.com/products/BTC-EUR/book?level=2
- Abfrageintervall: 5 Sekunden

### Kraken

- Referenz: https://www.kraken.com/features/api#get-order-book
- Abfrage folgender URLs:
    - https://api.kraken.com/0/public/Depth?pair=XBTUSD&count=10
    - https://api.kraken.com/0/public/Depth?pair=XBTEUR&count=10
- Abfrageintervall: 5 Sekunden
