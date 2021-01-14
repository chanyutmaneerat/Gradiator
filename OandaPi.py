import json
import requests
import time
import pprint
import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.positions as positions
from oandapyV20.contrib.requests import PositionCloseRequest
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import LimitOrderRequest
import oandapyV20.endpoints.instruments as instruments

access_token = '---------API KEY------------------'
account_id = '----------SECRET KEY----------------'
client = oandapyV20.API(access_token= access_token)
api = API(access_token = access_token)
params = {'instruments' : 'XAU_USD'}


def getTime():
  named_tuple = time.localtime() # get struct_time
  Time = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
  print(Time)
  print(' ')
  print('MA20 TRADING PI ', 'OANDA')
  
def get_Price_Bid():

  r = pricing.PricingInfo(account_id, params= params)
  rv = api.request(r)
  result = r.response
  result_price = result['prices'][0]['closeoutBid']
  return float(result_price)

def get_Price_Ask():
  r = pricing.PricingInfo(account_id,params=params)
  rv = api.request(r)
  result = r.response
  result_price = result['prices'][0]['closeoutAsk']
  return float(result_price)

def sum_Exposure():
  r = positions.PositionList(accountID = account_id)
  client.request(r)
  result = r.response
  result_units = result['positions'][0]['long']['units']
  return int(result_units)

def Total_Buy_Limit():
  r = orders.OrdersPending(accountID=account_id)
  client.request(r)
  result = r.response
  ordersPending = []
  for i in range(len(result['orders'])):
    if int(result['orders'][i]['units']) >= 0:
      ordersPending.append(int(result['orders'][i]['units']))
    else:
      ordersPending.append(0)

  return sum(ordersPending)

def Total_Sell_Limit():
  r = orders.OrdersPending(accountID=account_id)
  client.request(r)
  result = r.response
  ordersPending = []
  for i in range(len(result['orders'])):
    if int(result['orders'][i]['units']) < 0:
      ordersPending.append(int(result['orders'][i]['units']))
    else:
      ordersPending.append(0)

  return sum(ordersPending)

def get_average_price():
  r = positions.PositionList(accountID = account_id)
  client.request(r)
  result = r.response
  result_averagePrice = result['positions'][0]['long']['averagePrice']
  return result_averagePrice

def markUpExposure():
  bid = []
  ask = []
  markup = []
  maxExposure = []
  
  for b in range(960,2500,20):
    bid.append(b)
  
  for a in range(980,2520,20):
    ask.append(a)
  
  for m in range(40,1580,20):
    markup.append(m)
  markup.reverse()
  
  for i in range(len(markup)):
    if get_Price_Bid() > bid[i] and get_Price_Bid() < ask[i]:
      maxExposure.append(bid[i])    #maxExposure[0]
      maxExposure.append(ask[i])    #maxExposure[1]
      maxExposure.append(markup[i]) #maxExposure[2]
      return maxExposure


def create_orders(koi):
  result = koi*20
  getPrice = get_Price_Bid()
  getsumExposure = sum_Exposure()
  maxExposure = markUpExposure()
  getsignal = get_signal()
  totalBuyLimit = Total_Buy_Limit()
  totalSellLimit = Total_Sell_Limit()
  accountID = account_id
  client = API(access_token= access_token)
  pair = "XAU_USD"
  min_tprang = 20



  print('Total Buy Exposure =', 0,'$')
  print('Total Sell Exposure =',0,'$')
  print('Total Buy Limit =',totalBuyLimit, '$')
  print('Total Sell Limit =',totalSellLimit, '$')
  print('Sum Exposure =',getsumExposure, '$')
  print('Max Exposure =',maxExposure[2], '$', '(MarkUp)')
  print(' ')
  print(getsignal)

  if getsignal == 'BUYSIGNAL!' and (maxExposure[2] - getsumExposure)>= min_tprang and totalBuyLimit == 0 and totalSellLimit == 0:
    createOrders = LimitOrderRequest(instrument= pair,units=(maxExposure[2] - getsumExposure) + result,price= maxExposure[0] - result)
    r = orders.OrderCreate(accountID,data=createOrders.data)
    result = client.request(r)
    result1 = result['orderCreateTransaction']['id']
    result2 = result['orderCreateTransaction']['instrument']
    result3= result['orderCreateTransaction']['price']
    result4= result['orderCreateTransaction']['time']
    result5=result['orderCreateTransaction']['type']
    result6 = result['orderCreateTransaction']['units']
    print('BUYLIMIT !','ID :',result1, 'Sym :',result2, 'Price :',result3, result4, result5 ,'Units :',result6  )

  elif getsignal == "SELLSIGNAL!" and (getsumExposure - maxExposure[2])>= min_tprang and totalSellLimit == 0 and totalBuyLimit == 0 :
    if getPrice >= (maxExposure[1] + result) and (getsumExposure - maxExposure[2])>=min_tprang :
      closeOrder = positions.PositionClose(accountID,instrument= pair ,data= ordr.data)
      rv = client.request(closeOrder)
      rv1 = rv['longOrderCreateTransaction']['id']
      rv2 = rv['longOrderCreateTransaction']['time']
      rv3 = rv['longOrderCreateTransaction']['instrument']
      rv4 = rv['longOrderCreateTransaction']['units']
      # rv5 = rv['longOrderCreateTransaction']['type']
      # rv6 = rv['longOrderCreateTransaction']['units']
      print('SELLLIMIT !','ID :',rv1, 'Sym :',rv3,'Price',maxExposure[1],'Time',rv2 , 'Units',rv4)
  else:
    print('NO ACCTION')

      #return maxExposure 
def ma20_signal():
  params = {
    'count': 20,
    'granularity' : 'H4'
    }
  r = instruments.InstrumentsCandles(instrument = "XAU_USD",params= params)
  client.request(r)
  result = r.response
  all_close = []

  for i in range(len(result['candles'])):
    close = float(result['candles'][i]['mid']['c'])
    all_close.append(close)
      
  return (sum(all_close)/20)

def get_signal():
  getPrice = get_Price_Bid()
  ma20 = ma20_signal()
  if getPrice < ma20 :
    return 'BUYSIGNAL!'
  
  elif getPrice > ma20:
    return 'SELLSIGNAL!'

  

def order_price():
  r = orders.OrderList(account_id)
  client.request(r)
  result = r.response
  print(result)
  # order_list = result['orders'][0]['price']
  # return order_list

def order_ID():
  r = orders.OrderList(account_id)
  client.request(r)
  result = r.response
  #print(result)
  orderID = result['orders'][0]['id']
  return orderID 

def cancel_order():
  if Total_Buy_Limit() > 0 or Total_Sell_Limit() > 0 :
    # client = oandapyV20.API(access_token=access_token)
    r = orders.OrderCancel(accountID = account_id,orderID = order_ID())
    client.request(r)
    result = r.response
    cancelorder = result['orderCancelTransaction']
    print('id: {} [{}] type: {} '.format(cancelorder['id'],cancelorder['time'],cancelorder['type']))
  else:
    pass




pi = '314159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328238644709384'
pix = pi.replace('0','1')

lenpi = len(pix)
koi = 0
getsignal = get_signal()
getPrice = get_Price_Bid()
sumExposure = sum_Exposure()
all_signal = []
all_sumExposure = []
while True:
  
  getTime()
  getPrice = get_Price_Bid()
  getsignal = get_signal()
  ma20 = ma20_signal()
  print(' ')
  print("current Price => {} \nMA20 => {}".format(getPrice,ma20))
  print(' ')  

  if getsignal == "BUYSIGNAL!" or getsignal == "SELLSIGNAL!":
    all_signal.append(getsignal)
    all_sumExposure.append(sum_Exposure)
    
    if all_signal[0] == all_signal[-1] :
      create_orders(koi= int(pix[koi]))
      print(' ')

    else:
      cancel_order()
      koi += 1
      all_signal.clear()
    print('koi => {}'.format(koi))
    print('PI => {}'.format(pix[koi]))
  print('===============================================')
  time.sleep(30)


    





# koi =0
# d = 0
# all_signal = []
# while True :
#   print(pix[koi])

# while d <= lenpi:
#   getTime()
#   if get_Price_Bid() > order_price():
#     print(pix[koi])
#   else:
#     koi+=1
#     d+=1
#     print(pix[koi])
    

 


      
    







