#!/usr/bin/env python3

# Wartezeit für den ersten Crawler.
# Folgecrawler werden immer genau fünf Sekunden später gestartet
#
# Gültige Werte:
# - immediately                 Sofort starten
#
# - full_5_seconds              Zu vollen fünf Sekunden der
#                               Uhrzeit starten (z.B. 10 Uhr 00 Minuten 05 Sekunden 000 ms)
#
# - slightly_ahead_5_seconds    Kurz vor vollen fünf Sekunden der
#                               Uhrzeit starten (z.B. 10 Uhr 00 Minuten 04 Sekunden 500 ms)
# 
start_time_delay = "full_5_seconds"


# Sammel-API
aggregate_data_endpoint = "https://example.com/aggregate.php"


# Chunk-Größe
# 24 Datensätze = 2min = ca. 14-15 kB (Bitfinex) // 20-21 kB (Coinbase) // 22-23 kB (Bitstamp)
# 60 Datensätze = 5min = ca. 42-43 kB (Bitfinex) // 51-52 kB (Coinbase) // 56-57 kB (Bitstamp)
aggregate_data_chunk_size = 60
