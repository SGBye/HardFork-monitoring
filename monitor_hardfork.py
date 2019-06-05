import collections
import json
import statistics
import time

import websocket

while True:
    try:
        hardfork_timestamp = int(input("Enter the UNIX timestamp for HardFork: "))
    except ValueError:
        print("Please, enter a valid UNIX timestamp. For example: ")
        continue

    if hardfork_timestamp <= time.time():
        print("This time is already in the past! Try again.")
        continue
    else:
        break

print("Establishing connection...")
ws = websocket.create_connection("wss://ws.blockchain.info/inv")
print("Connection established!")
ws.send(json.dumps({"op": "blocks_sub"}))
print("Sending data...")
blocks_timestamps = collections.deque(maxlen=11)

while True:
    result = json.loads(ws.recv())
    print(f"Received block with hash {result['x']['hash']}. Calculating...")
    blocks_timestamps.append(result['x']['time'])
    if len(blocks_timestamps) == 11 and statistics.median(blocks_timestamps) >= hardfork_timestamp:
        print("The HardFork has come! Beware...")
        ws.close()
        break
    print("Waiting for another block...")