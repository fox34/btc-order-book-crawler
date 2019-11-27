
# Börsen abfragen und Daten aufbereiten
from abc import ABC, abstractmethod
import json
from math import floor
from SetInterval import SetInterval
from socket import getfqdn
from threading import Timer
from time import time
from urllib.parse import urlencode
import urllib.request

# Abstrakte Basis-Klasse ohne Code zur Aufbereitung einzelner Datensätze
class QueryExchange(ABC):

    # Klassen-Variablen, geteilt
    hostname = getfqdn()
    
    # API-Adresse des Sammelskriptes
    aggregate_data_endpoint = "https://research.noecho.de/btc-triangular-arbitrage/cron/order-book-5s.php"
    
    # Chunk-Größe
    # 24 Datensätze = 2min = ca. 14-15 kB (Bitfinex) // 20-21 kB (Coinbase) // 22-23 kB (Bitstamp)
    # 60 Datensätze = 5min = ca. 42-43 kB (Bitfinex) // 51-52 kB (Coinbase) // 56-57 kB (Bitstamp)
    aggregate_data_chunk_size = 60
    
    
    # Init: Instanz-Variablen, Bezeichnung und API-URL festlegen
    def __init__(self, name, api_url):
        
        # Instanz-Variablen, KEINE (geteilten) Klassen-Variablen!!!
        self.aggregate_data = []
        
        # Eigenschaften festlegen
        self.name = name
        self.api_url = api_url
        
        print(
            "Initialisiere", name,
            "- Chunk-Size:", self.aggregate_data_chunk_size,
            "- Host:", self.hostname
        )
        
        # Starte Intervall und sofort (asynchron)
        SetInterval(self.request_interval, self.query)
        Timer(0, self.query).start()
    
    
    # Börse abfragen
    def query(self):
        
        # Bitfinex mag python-User-Agents nicht...
        req = urllib.request.Request(
            self.api_url,
            headers = {
                'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15"
            }
        )
        
        # Börse abfragen
        try:
            with urllib.request.urlopen(req) as response:
                self.aggregate_data.append(self.prepare_dataset(response.read()))
        except urllib.error.HTTPError as e:
            print("!!! Error while querying the exchange!", self.api_url, e.code, e.reason)
            # TODO Fehlerbehandlung? Logging? Lücken sind eigentlich zu vermeiden
        
        
        #print(self.name, self.aggregate_data)
        
        # Nach x Datensätzen an Sammelskript senden
        if (len(self.aggregate_data) >= self.aggregate_data_chunk_size):
            self.send_to_collector()
    
    
    # Daten an Sammelskript senden
    def send_to_collector(self):
        
        # Daten aufbereiten
        send_data = urlencode({
            "source_host": self.hostname,
            "exchange": self.name,
            "raw_data": json.dumps(self.aggregate_data)
        })
        send_data = send_data.encode("ascii")
        
        # Interne Daten zurücksetzen
        self.aggregate_data = []
        #print("Sending aggregate", send_data)
        
        req = urllib.request.Request(self.aggregate_data_endpoint, send_data)
        
        # TODO Gesendete Daten bei Fehler behalten / Anfrage wiederholen?!
        try:
            with urllib.request.urlopen(req) as response:
                #print(response.read())
                print("{:10.6f}".format(time()), self.name, round(len(send_data)/1000, 1), "kB an Sammel-API, HTTP-Code", response.getcode())
                if response.getcode() != 200:
                    print("Error message:", response.read())
        except urllib.error.HTTPError as e:
            print("!!! Error while sending results!", e.code, e.reason)
            # TODO Fehlerbehandlung, Logging
    
    # Daten aufbereiten
    @abstractmethod
    def prepare_dataset(self, dataset):
        pass


# https://www.bitstamp.net/api/
class BitstampExchange(QueryExchange):
    
    # Abfrageintervall in Sekunden
    # Berücksichtigen, dass jede Börse i.d.R. direkt 2x abgefragt wird: EUR+USD
    # Limit: 8.000 pro 10 Minuten = 800 pro Minute = 13,3 pro Sekunde, Stand 07.11.2019
    request_interval = 5
    
    # Datensatz aufbereiten
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
        
        # JSON hat bereits richtige Struktur
        dataset = json.loads(dataset)
        
        # Timestamp auf Millisekunden-Basis
        dataset['timestamp'] = time()
        
        # Beschränke auf 10 Bids+Asks
        dataset['bids'] = dataset['bids'][0:10]
        dataset['asks'] = dataset['asks'][0:10]
        
        return dataset


# https://docs.bitfinex.com/reference
class BitfinexExchange(QueryExchange):
    
    # Abfrageintervall in Sekunden
    # Berücksichtigen, dass jede Börse i.d.R. direkt 2x abgefragt wird: EUR+USD
    # Limit (für Order Books): 30 pro Minute = alle 2 Sekunden, Stand 07.11.2019
    request_interval = 5
    
    # Datensatz aufbereiten
    def prepare_dataset(self, dataset):
        # https://docs.bitfinex.com/reference#rest-public-books
        # Amount >0 = BID / <0 = ASK
        # 
        # Preis, Anzahl Aufträge, Anzahl Bitcoins (Price, Count, Amount)
        # Erst Bids nach Preis absteigend, dann Asks nach Preis aufsteigend
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
        
        # Sicherheitshalber als String, da Menge im Original-JSON float ist
        for order in dataset:
            if order[2] > 0:
                # BID
                result['bids'].append([order[0], str(order[2])])
                
            else:
                # ASK
                result['asks'].append([order[0], str(-order[2])])
        
        # Beschränke auf 10 Bids+Asks
        result['bids'] = result['bids'][0:10]
        result['asks'] = result['asks'][0:10]
        
        return result


# Achtung: Unterschied Pro-API und Basis-API
# https://docs.pro.coinbase.com
class CoinbaseExchange(QueryExchange):
    
    # Abfrageintervall in Sekunden
    # Berücksichtigen, dass jede Börse i.d.R. direkt 2x abgefragt wird: EUR+USD
    # Limit: 3 Abfragen pro Sekunde, Stand 07.11.2019
    request_interval = 5
    
    # Datensatz aufbereiten
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
        
        # Beschränke auf 10 Bids+Asks
        dataset['bids'] = dataset['bids'][0:10]
        dataset['asks'] = dataset['asks'][0:10]
        
        # Nur Preis + Ordergröße benötigt
        for order in dataset['bids']:
            result['bids'].append([order[0], order[1]])
            
        for order in dataset['asks']:
            result['asks'].append([order[0], order[1]])
        
        return result
