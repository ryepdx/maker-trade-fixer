#! /usr/bin/python3

import json
from web3 import Web3, RPCProvider
from operator import itemgetter

precision = 1000000000000000000

web3rpc = Web3(RPCProvider())

web3rpc.eth.defaultAccount = "0xb19b144df98dc6cf672ec405d6c0816511cfa37f"
web3rpc.eth.defaultBlock = "latest"
# Can also be an integer or one of "latest", "pending", "earliest"

with open('simple_market.abi', 'r') as abi_file:
  abi_json = abi_file.read().replace('\n','')

abi = json.loads(abi_json)

#repston
#contract = web3rpc.eth.contract(abi, address="0x0bC603C1e35e0A7C16623230b2C10cA1668cb0C8")

#live
contract = web3rpc.eth.contract(abi, address="0xa1B5eEdc73a978d181d1eA322ba20f0474Bb2A25")

last_offer_id = contract.call().last_offer_id()

id = 0
offers = []

while id <  last_offer_id + 1:
  offers.append(contract.call().offers(id))
  id = id + 1

id=0

buy_orders = []
sell_orders = []

for offer in offers:
  valid = offer[5]
  if valid:
    sell_how_much = float(offer[0]) / precision
    sell_which_token = offer[1]
    buy_how_much = float(offer[2]) / precision
    buy_which_token = offer[3]
    owner = offer[4][2:8]

    if sell_which_token == "0xc66ea802717bfb9833400264dd12c2bceaa34a6d":
      s_token = "MKR"
    elif sell_which_token == "0xa74476443119A942dE498590Fe1f2454d7D4aC0d":
      s_token = "W-GNT"
    else:
      s_token = "W-ETH"

    if buy_which_token == "0xc66ea802717bfb9833400264dd12c2bceaa34a6d":
      b_token = "MKR"
    elif buy_which_token == "0xa74476443119A942dE498590Fe1f2454d7D4aC0d":
      b_token = "W-GNT"
    else:
      b_token = "W-ETH"

    if s_token == "MKR" and b_token == "W-ETH":
      sell_orders.append([id, sell_how_much, buy_how_much/sell_how_much, buy_how_much, owner])

    if s_token == "W-ETH" and b_token == "MKR":
      buy_orders.append([id, buy_how_much, sell_how_much/buy_how_much, buy_how_much, owner])
    id = id + 1

buy_orders.sort(key=itemgetter(2), reverse=True)
bid = float(buy_orders[0][2])
bq  = float(buy_orders[0][1]) 
print ("Biding for %0.5f MKR @ %0.5f ETH/MKR" % (bq,bid))

sell_orders.sort(key=itemgetter(2), reverse=False)
ask = float(sell_orders[0][2])
aq  = float(sell_orders[0][1]) 
print ("Asking for %0.5f MKR @ %0.5f ETH/MKR" % (aq,ask))

if bid >= ask:
  if bq > aq:
    print ("Buy from Sell book and sell to Buy book")
  else:
    print ("Buy from Buy book and sell to Sell book")
else:
 print ("All is well")
