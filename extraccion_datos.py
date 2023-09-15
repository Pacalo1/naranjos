from binance.client import Client
import time
client= Client(api_key='SgLRNVSNnn8J1KMIjJeG0i4LBEMzcwcJfFpqJHgQHSQXRFjWMER1lySJ5LJHNOb2',api_secret='FtIR9C1xdTosRPDxtN7WCHZaMP7c9g114RHjpVHwmNfIsVfOawiXHoCoseOzv8lD')
datos=client.get_historical_trades(symbol='BTCUSDC',limit=1000)
print(datos[0])

x=0
while(x==0):
    time.sleep(2)
    client= Client(api_key='SgLRNVSNnn8J1KMIjJeG0i4LBEMzcwcJfFpqJHgQHSQXRFjWMER1lySJ5LJHNOb2',api_secret='FtIR9C1xdTosRPDxtN7WCHZaMP7c9g114RHjpVHwmNfIsVfOawiXHoCoseOzv8lD')
    datos=client.get_historical_trades(symbol='BTCUSDC',limit=1000)
    precio =datos[0]
    precio=precio['price']
    print(precio)

