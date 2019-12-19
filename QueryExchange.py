from abc import ABC, abstractmethod
import config
import json
import logging
from math import floor
from SetInterval import SetInterval
from socket import getfqdn
from threading import Timer
from time import time
from urllib.parse import urlencode
import urllib.request

# Abstract query class without knowledge of custom exchange data formats
class QueryExchange(ABC):
    
    # Hostname, useful if several crawlers are being used
    hostname = getfqdn()
    
    # Set instance variables, crawler name, API URL
    def __init__(self, name, api_url):
        
        # Current buffer
        self.aggregate_data = []
        
        # Crawler properties
        self.name = name
        self.api_url = api_url
        
        logging.info(
            name + 
            " - Chunk size: " + str(config.aggregate_data_chunk_size) + 
            " - Host: " + self.hostname
        )
        
        # Start asynchronously
        self.interval = SetInterval(self.request_interval, self.query)
        Timer(0, self.query).start()
    
    # Shutdown activity, send remaining data to collector
    def shutdown(self):
        self.interval.cancel()
        self.send_to_collector()
    
    # Query exchange
    def query(self):
        
        # Bitfinex denies python user agents
        # Kraken uses "Browser Integrity Check"
        req = urllib.request.Request(
            self.api_url,
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Connection': 'keep-alive'
            }
        )
        
        # Send query
        try:
            with urllib.request.urlopen(req) as response:
                self.aggregate_data.append(self.prepare_dataset(response.read()))
        except urllib.error.HTTPError as e:
            logging.error("Error while querying " + self.api_url + " " + str(e.code) + e.reason)
            # TODO Error handling
        except urllib.error.URLError as e:
            logging.error("Error while querying " + self.api_url + " " + str(e.code) + e.reason)
            # TODO Error handling
        
        #print(self.name, self.aggregate_data)
        
        # Send buffer to collector
        if (len(self.aggregate_data) >= config.aggregate_data_chunk_size):
            self.send_to_collector()
    
    
    # Send buffer to collector
    def send_to_collector(self):
        
        if len(self.aggregate_data) == 0:
            print("Nothing to send.")
            return
        
        # Build POST request data
        send_data = urlencode({
            "source_host": self.hostname,
            "exchange": self.name,
            "raw_data": json.dumps(self.aggregate_data)
        })
        send_data = send_data.encode("ascii")
        
        # Reset buffer
        self.aggregate_data = []
        #print("Sending aggregate", send_data)
        
        req = urllib.request.Request(config.aggregate_data_endpoint, send_data)
        
        # TODO Error handling
        try:
            with urllib.request.urlopen(req) as response:
                #print(response.read())
                logging.info(self.name + " " + str(round(len(send_data)/1000, 1)) + "kB to aggregation API, HTTP-Code " + str(response.getcode()))
                if response.getcode() != 200:
                    logging.error("HTTP != 200, Error message: " + response.read())
        except urllib.error.HTTPError as e:
            logging.error("Error while sending results! " + str(e.code) + e.reason)
        except urllib.error.URLError as e:
            logging.error("Error while querying the exchange! " + str(e.code) + e.reason)

        
    # Parse exchange response
    @abstractmethod
    def prepare_dataset(self, dataset):
        pass


# https://www.bitstamp.net/api/
class BitstampExchange(QueryExchange):
    
    # Request interval in seconds
    # Reminder: Each exchange will be queried twice a second (EUR + USD)
    # Limit: 8.000 in 10 minutes = 800 per minute = 13,3 per second as of 2019-11-07
    request_interval = 5
    
    # Parse exchange response
    def prepare_dataset(self, dataset):
        # https://www.bitstamp.net/api/
        # {
        #     "timestamp": "1573126947",
        #     "bids": [
        #         ["9186.35", "0.47870000"],
        #         ["9186.34", "0.03489748"],
        #         ...
        #     ],
        #     "asks": [
        #         ["9197.07", "0.99000000"],
        #         ["9197.55", "5.44140000"],
        #         ...
        #     ]
        # }
        
        # Response has correct structure
        dataset = json.loads(dataset)
        
        # Timestamp in milliseconds
        dataset['timestamp'] = time()
        
        # Limit to 10 bids+asks
        dataset['bids'] = dataset['bids'][0:10]
        dataset['asks'] = dataset['asks'][0:10]
        
        return dataset


# https://docs.bitfinex.com/reference
class BitfinexExchange(QueryExchange):
    
    # Request interval in seconds
    # Reminder: Each exchange will be queried twice a second (EUR + USD)
    # Limit (order books): 30 per minute as of 2019-11-07
    request_interval = 5
    
    # Parse exchange response
    def prepare_dataset(self, dataset):
        # https://docs.bitfinex.com/reference#rest-public-books
        # Amount >0 = BID / <0 = ASK
        # 
        # Price, NumOffers, Amount
        # Sorted by bids descending, then asks ascending
        # [
        #     [9205.1, 2, 1.30681808]
        #     [9205.0, 1, 0.4],
        #     ...,
        #     [9205.2, 5, -2.63099555],
        #     [9205.6, 1, -0.0099912],
        #     ...
        # ]
        result = {
            "timestamp": time(),
            "bids": [],
            "asks": []
        }
        
        dataset = json.loads(dataset)
        
        # For maximum precision: handle float as string to prevent unwanted rounding
        for order in dataset:
            if order[2] > 0:
                # BID
                result['bids'].append([order[0], str(order[2])])
                
            else:
                # ASK
                result['asks'].append([order[0], str(-order[2])])
        
        # Limit to 10 bids+asks
        result['bids'] = result['bids'][0:10]
        result['asks'] = result['asks'][0:10]
        
        return result


# https://docs.pro.coinbase.com
class CoinbaseExchange(QueryExchange):
    
    # Request interval in seconds
    # Reminder: Each exchange will be queried twice a second (EUR + USD)
    # Limit: 3 requests per second as of 2019-11-07
    request_interval = 5
    
    # Parse exchange response
    def prepare_dataset(self, dataset):
        # https://docs.pro.coinbase.com/#get-product-order-book
        # {
        #     "sequence": 11192389945,
        #     "bids": [
        #         ["9194.77", "6.2242097",9],
        #         ["9194.5", "0.01", 1],
        #         ...
        #     ],
        #     "asks": [
        #         ["9194.78", "2.8115731", 5],
        #         ["9195.78", "0.2", 1],
        #         ...
        #     ]
        # }
        
        result = {
            "timestamp": time(),
            "bids": [],
            "asks": []
        }
        
        dataset = json.loads(dataset)
        
        # Limit to 10 bids+asks
        dataset['bids'] = dataset['bids'][0:10]
        dataset['asks'] = dataset['asks'][0:10]
        
        # Keep only price and order size
        for order in dataset['bids']:
            result['bids'].append([order[0], order[1]])
            
        for order in dataset['asks']:
            result['asks'].append([order[0], order[1]])
        
        return result


# https://www.kraken.com/features/api#get-order-book
class KrakenExchange(QueryExchange):
    
    # Request interval in seconds
    # Reminder: Each exchange will be queried twice a second (EUR + USD)
    # Limit Stand 02.12.2019:
    # Counter for each request +1
    # Counter is reduced by 1 each 3 seconds
    # Counter limit: 15
    # ???
    request_interval = 5
    
    # Parse exchange response
    def prepare_dataset(self, dataset):
        # https://www.kraken.com/features/api#get-order-book
        # <price>,<volume>,<timestamp>
        # {
        #     "error": [],
        #     "result": {
        #         "XXBTZUSD": {
        #             "asks": [
        #                 ["7347.60000", "0.630", 1575296019],
        #                 ["7350.00000", "8.486", 1575296021],
        #                 ...
        #             ],
        #             "bids": [
        #                 ["7347.50000", "10.928", 1575296021],
        #                 ["7346.00000", "0.307", 1575296019],
        #                 ...
        #             ]
        #         }
        #     }
        # }
        
        result = {
            "timestamp": time(),
            "bids": [],
            "asks": []
        }
        
        dataset = json.loads(dataset)
        if dataset['error']:
            logging.error("Kraken error: " + dataset['error'])
            return result
        
        dataset = dataset['result']
        
        set_name = list(dataset)[0]
        
        # Keep only price and order size
        for order in dataset[set_name]['bids']:
            result['bids'].append([order[0], order[1]])
            
        for order in dataset[set_name]['asks']:
            result['asks'].append([order[0], order[1]])
        
        return result
