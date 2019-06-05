import collections
import json
import logging
import statistics
import time

import websocket

logging.basicConfig(
    format="%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

WS_SUBSCRIBE_URL = "wss://ws.blockchain.info/inv"
BLOCKS_FOR_MTP = 11

while True:
    hardfork_timestamp = input("Enter the UNIX timestamp for HardFork: \n")
    logging.debug("The input value is '%s'", hardfork_timestamp)
    try:
        hardfork_timestamp = int(hardfork_timestamp)
    except ValueError:
        logging.error("An exception during handling '%s' input has happened", hardfork_timestamp)
        logging.info("Please, enter a valid UNIX timestamp. For example: 1559708603")
        continue

    if hardfork_timestamp <= time.time():
        logging.info("This time is already in the past! Try again.")
        continue
    else:
        break

logging.info("Establishing connection...")
ws = websocket.create_connection(WS_SUBSCRIBE_URL)
logging.info("Connection established!")
ws.send(json.dumps({"op": "blocks_sub"}))
logging.info("Sending data...")

blocks_timestamps = collections.deque(maxlen=BLOCKS_FOR_MTP)

while True:
    logging.info("Waiting for a block...")
    result = json.loads(ws.recv())
    logging.info("Received block with hash %s. Calculating...", result['x']['hash'])
    blocks_timestamps.append(result['x']['time'])
    if len(blocks_timestamps) == BLOCKS_FOR_MTP and statistics.median(blocks_timestamps) >= hardfork_timestamp:
        logging.info("The HardFork has come! Beware...")
        ws.close()
        break
