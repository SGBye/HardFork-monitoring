import collections
import json
import logging
import statistics
import time

import requests
import websocket


def get_blocks_url(time_msec):
    return f"https://blockchain.info/blocks/{time_msec}?format=json"


logging.basicConfig(
    format="%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)


TIME_NOW_MS = int(round(time.time() * 1000))
GET_TO_YESTERDAY = 43200000  # 12 hours
GET_DAY_BLOCKS_URL = get_blocks_url(TIME_NOW_MS)
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

# first get 11 latest blocks and check their median time not to miss anything
# the blocks are sorted from the newest to the oldest
r = requests.get(GET_DAY_BLOCKS_URL)
blocks_times = collections.deque((block['time'] for block in r.json()['blocks'][:BLOCKS_FOR_MTP]), maxlen=BLOCKS_FOR_MTP)

# if you turn your program early in the morning, there won't be 11 blocks, so get the latest from yesterday
if len(blocks_times) < BLOCKS_FOR_MTP:
    need_more = BLOCKS_FOR_MTP - len(blocks_times)
    r = requests.get(get_blocks_url(TIME_NOW_MS - GET_TO_YESTERDAY))  # get back to past day

    # append the blocks to the right coz they are older
    blocks_times.append(block['time'] for block in r.json()['blocks'][:need_more])

if statistics.median(blocks_times) >= hardfork_timestamp:
    logging.info("The HardFork has come! Beware...")
    raise SystemExit("Thank you for using our program")

logging.info("HardFork hasn't come yet.")
logging.info("Establishing connection...")
ws = websocket.create_connection(WS_SUBSCRIBE_URL)
logging.info("Connection established!")
ws.send(json.dumps({"op": "blocks_sub"}))
logging.info("Sending data...")


while True:
    logging.info("Waiting for a block...")
    print(blocks_times)
    result = json.loads(ws.recv())
    logging.info("Received block with hash %s. Calculating...", result['x']['hash'])

    blocks_times.appendleft(result['x']['time'])  # append left coz it's sorted from the newest to the oldest

    if statistics.median(blocks_times) >= hardfork_timestamp:
        logging.info("The HardFork has come! Beware...")
        ws.close()
        raise SystemExit("Thank you for using our program")
