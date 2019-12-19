#!/usr/bin/env python3

# Start time delay for first crawler
# Next crawler will be started exactly five seconds later.
#
# Valid values:
# - immediately                 Do not wait
#
# - full_5_seconds              Wait for next five seconds, e.g. 10:00:05.000
#
# - slightly_ahead_5_seconds    Start slightly ahead of next five seconds, e.g. 10:00:04.500
#                               Useful for exchanges with response delays of more than one second
# 
start_time_delay = "full_5_seconds"


# Send data as POST request to this endpoint (any local or remote address)
aggregate_data_endpoint = "https://example.com/aggregate.php"


# Chunk size
# 24 datasets = 2 minutes = approx. 14-15 kB (Bitfinex) // 20-21 kB (Coinbase) // 22-23 kB (Bitstamp)
# 60 datasets = 5 minutes = approx. 42-43 kB (Bitfinex) // 51-52 kB (Coinbase) // 56-57 kB (Bitstamp)
aggregate_data_chunk_size = 60
