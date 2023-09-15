from binance import ThreadedWebsocketManager

def men(msg):
    print('hola')

def main():
    sim='BTCUSDT'
    twm=ThreadedWebsocketManager(api_key='SgLRNVSNnn8J1KMIjJeG0i4LBEMzcwcJfFpqJHgQHSQXRFjWMER1lySJ5LJHNOb2',api_secret='FtIR9C1xdTosRPDxtN7WCHZaMP7c9g114RHjpVHwmNfIsVfOawiXHoCoseOzv8lD')
    twm.start()
    print('va')

    twm.start_symbol_ticker_socket(callback=men,symbol=sim)
    
    twm.join()



if __name__ == "__main__":
    main()
