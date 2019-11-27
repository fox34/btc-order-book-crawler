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

