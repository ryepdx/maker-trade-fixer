#! /usr/bin/python3

import json
from web3 import Web3, RPCProvider
from operator import itemgetter

precision = 1000000000000000000

mkr_addr = "0xc66ea802717bfb9833400264dd12c2bceaa34a6d"
weth_addr = "0xC66eA802717bFb9833400264Dd12c2bCeAa34a6d"

web3rpc = Web3(RPCProvider())

web3rpc.eth.defaultAccount = "0xb19b144df98dc6cf672ec405d6c0816511cfa37f"
web3rpc.eth.defaultBlock = "latest"
# Can also be an integer or one of "latest", "pending", "earliest"

with open('simple_market.abi', 'r') as abi_file:
  abi_json = abi_file.read().replace('\n','')
abi = json.loads(abi_json)
market_contract = web3rpc.eth.contract(abi, address="0xa1B5eEdc73a978d181d1eA322ba20f0474Bb2A25")

with open('erc20.abi', 'r') as abi_file:
  abi_json = abi_file.read().replace('\n','')
abi = json.loads(abi_json)
weth_contract = web3rpc.eth.contract(abi, address="0xECF8F87f810EcF450940c9f60066b4a7a501d6A7")
mkr_contract = web3rpc.eth.contract(abi, address="0xC66eA802717bFb9833400264Dd12c2bCeAa34a6d")

weth_balance = float(weth_contract.call().balanceOf("0x6E39564ecFD4B5b0bA36CD944a46bCA6063cACE5"))/precision
mkr_balance  = float(mkr_contract.call().balanceOf("0x6E39564ecFD4B5b0bA36CD944a46bCA6063cACE5"))/precision

print("Balance available to the fixer: %0.5f ETH - %0.5f MKR\n" % (weth_balance, mkr_balance))

last_offer_id = market_contract.call().last_offer_id()

id = 0
offers = []

while id <  last_offer_id + 1:
  offers.append(market_contract.call().offers(id))
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
print ("Highest bid is for %0.5f MKR @ %0.5f ETH/MKR" % (bq,bid))

sell_orders.sort(key=itemgetter(2), reverse=False)
ask = float(sell_orders[0][2])
aq  = float(sell_orders[0][1]) 
print ("Lowest ask is for %0.5f MKR @ %0.5f ETH/MKR" % (aq,ask))

if bid >= ask:
  print("\nAction needed!")
  if bq > aq:
    print ("Buy from Ask book and sell to Bid book")
  else:
    print ("Buy from Bid book and sell to Ask book")
    if mkr_balance < bq:
      market_contract.call().Trade(mkr_balance, mkr_addr, bq*mkr_balance, weth_addr)
else:
 print ("All is well")
