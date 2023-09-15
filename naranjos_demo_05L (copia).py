###NOTA: si cambiamos el nombre de archivo name.py por name.pyw ya no nos abre la consola detras cuando lo ejecutamos desde windows
#naranjos_demo_0.1   - esta la interfaz y compra venta en demo hecho
#naranjos_demo_0.2   - cambiamos el websocked por simplemente hacerle llamadas al api cad 2 segundos para que nos de el precio
#naranjos_demo_0.3    --- estoy provando con el generador de eventos threading
#naranjos_demo_0.4    --- compra ya en serio...jjjjj
#naranjos_demo_0.5    --- vamos a meterle las estadisticas

from ctypes.wintypes import HLOCAL
from operator import truediv
from telnetlib import XASCII
from tkinter import *
from tokenize import Double

from binance.client import Client
from binance import ThreadedWebsocketManager
import time
import sqlite3
import threading
from datetime import datetime

#***************************************************************************************************************
#*********************************************CONSTANTES E INPUTS DEL PROGRAMA************************************************************
#*************************************************************************************************************** 
rango_mayor=30000 #el precio maximo para los naranjos
rango_menor=10000  # el precio minimo para los naranjos
take= 1 # porcentage del take
balance_inicial= 20 # el capital que tendra cada naranjo al principio
naranjos_numero=100 # el numero de naranjos que vamos a tener

bd_creada= True # si ya esta creada no la creamos de nuevo
bd_llena =True  # si la base de datos ya esta llena no la llenamos al principio
                # si es la primera vez que enchufamos esto habrá que decirle que es false para que la llene con los parametros de crea_naranjos
                # si la creamos de nuevo la tenemos que borrar antes( y guardarlo en el dbbroser)
Permitir_ordenes=True # Para ver si es la demo y no compramos o esta en produccion y le dejamos operar


#***************************************************************************************************************
#*********************************************VARIABLES************************************************************
#*************************************************************************************************************** socket_precio
socket_precio=0 


#------------------------------------variables para los naranjos-----------------------------------------------

naranjos_suma_precio = 0#  el precio que van a tener todas las particiones si se cierran bien
naranjos_precio_entrada=[0]*100 # creamos la lista con 100 elementos con valor cero para meter a que precio sera la orden de entrada
naranjo_take=[0]*100      #para sacar el precio de salida de cada naranjo
naranjo_dentro=[0]*100       #para saber si estamos dentro en eses precio
naranjo_numero_operaciones=[0]*100  # el numero de operaciones "cerradas" que ha tenido este naranjo
naranjo_balance=[0]*100
naranjo_porcentage_balance=[0]*100
naranjo_cantidad_comprar=[0]*100 # aqui meteremos la cantidad de BTC a comprar para que sea el valor del balance un USDT
naranjo_cantidad_comprar_real=[0]*100 # aqui metemos la cantidad de btc que hemos comprado realmete en la ultima orden

#*************************************variables para el interfaz************************************************

prueva=[1] #1ª label con el numero del naranjo
label_precio_entrada =[1] # aqui va el precio de entrada 
label_precio_take =[1]     # aqui va la orden de salida
label_naranjo_dentro = [1] 
label_naranjo_numero_operaciones = [1]
label_naranjo_balance= [1]
label_porcentage_balance=[1]
label_naranjo_en_precio=[1]  # le meteremos un flecha en el naranjo que este el precio

#****************************************variables de control**************************

#****************************************variables de balances**************************
balance_total =21  # metemos el balance total de todos lod naranjos, aunque se hayan quedado pilladas las ordenes

#****************************************variables varias...jjjjjjjjjjjjjjjjj******************************
minuto_anterior= 63  # esta variables la usamos para ver si ha cambiado el minuto y entrar en estadisticas() 


#***************************************************************************************************************
#*********************************************conectamos con la API de Binance************************************************************
#***************************************************************************************************************
# metemos todos los datos de los naranjos


key1='SgLRNVSNnn8J1KMIjJeG0i4LBEMzcwcJfFpqJHgQHSQXRFjWMER1lySJ5LJHNOb2'
key2='X17ftbqNdUgtAusjm25JFkkN6nasNM7XddQKfFgULmNjyFtP83XowxsrRKWLETqg'
secret1='FtIR9C1xdTosRPDxtN7WCHZaMP7c9g114RHjpVHwmNfIsVfOawiXHoCoseOzv8lD'
secret2='aS0tYCuhfCntbEWCff1QeH2p0sz4RP7A7na0Td3nrbbiGshQCEDAw7bp9um4sBwP'
client= Client(api_key=key2,api_secret=secret2)




#***************************************************************************************************************
#*********************************************Base de datos************************************************************
#***************************************************************************************************************
# metemos todos los datos de los naranjos



def db():
    bd_conexion=sqlite3.connect("naranjos")
    bd_cursor=bd_conexion.cursor()
    # Creamos la tabla, lo hacemos solo una vez..por eso lo pasamos a comentario
    #bd_cursor.execute("CREATE TABLE NARANJOS (numero_naranjo INTEGER ,precio_entrada DOUBLE,precio_take DOUBLE,dentro BOOL,numero_operaciones INTEGER,balance DOUBLE,porcentage_balance DOUBLE,cantidad_comprar DOUBLE)")
    
    #-------------------metemos un registro en la tabla
    #bd_cursor.execute("INSERT INTO NARANJOS VALUES(0,2000,2001,True,0,20,20,00.2)")
    
    #-------------------metemos muchos registros en la tabla-----------------------------
    
    for x in range(100):

       numero_naranjo=x
       precio_entrada= naranjos_precio_entrada[x]
       take_aqui=naranjo_take[x]
       dentro= naranjo_dentro[x]
       numero_operaciones=naranjo_numero_operaciones[x]
       balance=naranjo_balance[x]
       porcentage_balance=naranjo_porcentage_balance[x]
       cantidad_comprar=naranjo_cantidad_comprar[x]



      
       bd_cursor.execute("INSERT INTO NARANJOS VALUES(?,?,?,?,?,?,?,?)",(numero_naranjo,precio_entrada,take_aqui,dentro,numero_operaciones,balance,porcentage_balance,cantidad_comprar))
       bd_conexion.commit()

    print(' Bd llena')
    bd_conexion.close()


#***************************************************************************************************************
#*********************************************Cada Tick************************************************************
#***************************************************************************************************************
# cada vez que haya un nuevo precio pasara por aqui...metemos la funcion en mensage socket, que es donde nos da el nuevo precio

def cada_tick():

   global socket_precio 
   global balance_total
   balance_total=0  # inicialicamos el balance total para que empiece a sumarlo desde 0
   balance_porcentage=0

   for x in range(100):         
        #-------------miramos haber si tiene que entrar en algun precio de algun naranjo
        if  naranjo_dentro[x] == False and float(socket_precio) > naranjos_precio_entrada[x] and float(socket_precio) < (naranjos_precio_entrada[x] + 15) : 
            naranjo_dentro[x] =True
            label_naranjo_dentro[x].config(text="D")
            label_naranjo_dentro[x].config(fg='#22b486')
            
            #-----------EJECUTAMOS LA ORDEN DE COMPRA-----------
            cantidad_a_comprar=naranjo_balance[x] / float(socket_precio) # para saber exactamente lo que tenemos que comprar con el precio actual
            
            if Permitir_ordenes== True:   # preguntamos si dejamos operar
               
               
               cantidad_a_comprar=float(round(cantidad_a_comprar,5))
               naranjo_cantidad_comprar[x]=cantidad_a_comprar
               print (cantidad_a_comprar)
               order=client.order_market_buy(symbol='BTCUSDT',quantity=cantidad_a_comprar)



            #-----------------CAMBIAMOS LOS REGISTROS DE LA BD----------
            
            bd_conexion=sqlite3.connect('naranjos')
            bd_cursor=bd_conexion.cursor()
            #----------cambiamos el dato de fuera a dentro
            bd_dato_dentro=True
            bd_dato_id=x   
            bd_query="UPDATE NARANJOS SET dentro= ? WHERE numero_naranjo = ?"
            bd_cursor.execute(bd_query,(bd_dato_dentro,bd_dato_id))
            bd_conexion.commit()
            #----------cambiamos la cantidad de btc que hemos comprado------
            bd_dato_id=x   
            bd_query="UPDATE NARANJOS SET cantidad_comprar= ? WHERE numero_naranjo = ?"
            bd_cursor.execute(bd_query,(cantidad_a_comprar,bd_dato_id))
            bd_conexion.commit()



            bd_conexion.close()

        
        #-------------vamos a ir sumando el balance de cada naranjo (lo hace siempre para que despues de cada tick tengamos el balance total)
        balance_total=balance_total +  naranjo_balance[x]
        
        #--------------si  el naranjo esta dentro calculamos su porcentaje de balance
        if naranjo_dentro[x] == True :
            porcentage= (float(socket_precio) * 100) / float(naranjos_precio_entrada[x])
            
            naranjo_porcentage_balance[x]=(porcentage * float(naranjo_balance[x])) / 100
            precio=str(naranjo_porcentage_balance[x])[0:5]
            label_porcentage_balance[x].config(text=precio)
        
        #--------------sacamos el balance del porcentage
        balance_porcentage=balance_porcentage +  naranjo_porcentage_balance[x]
        balance_porcentage_s=str(balance_porcentage)[0:7]

        #---------------- metemos la flechita donde este el precio
        
        label_naranjo_en_precio[x].config(text=" ")
        if float(socket_precio) > naranjos_precio_entrada[x] and float(socket_precio) < naranjos_precio_entrada[x + 1] :
            label_naranjo_en_precio[x].config(text="<---")
   
        #----------------- miramos si hay algun naranjo que este dentro y tenga que salir

        if naranjo_dentro[x] == True and  float(socket_precio) > naranjo_take[x] :
            balance_nuevo=float(socket_precio) * naranjo_cantidad_comprar[x] # para saber exactamente a que precio real compramos
            naranjo_balance[x] = balance_nuevo
            #------------------EJECUTAMOS LA ORDEN DE VENTA------------------
            cantidad_a_comprar=naranjo_cantidad_comprar[x]
            cantidad_a_comprar=float(round(cantidad_a_comprar,5))
            order=client.order_market_sell(symbol='BTCUSDT',quantity=cantidad_a_comprar)
            
            
            
            naranjo_dentro[x]= False
            naranjo_numero_operaciones[x]=naranjo_numero_operaciones[x] + 1
            
            
            
            naranjo_balance[x]= balance_nuevo
            label_naranjo_dentro[x].config(text="F")
            label_naranjo_dentro[x].config(fg='#f5888e')
            label_naranjo_numero_operaciones[x].config(text=naranjo_numero_operaciones[x])
            
            text_balance=str(naranjo_balance[x])
            text_balance=text_balance[0:6]
            label_naranjo_balance[x].config(text=text_balance)
            naranjo_cantidad_comprar[x]= naranjo_balance[x]/ naranjos_precio_entrada[x]


             #-----------------cambiamos los registros de la bd----------
            bd_conexion=sqlite3.connect('naranjos')
            bd_cursor=bd_conexion.cursor()
            #-cambiamos de Dentro a Fuera
            bd_dato_dentro=False
            bd_dato_id=x


            bd_query="UPDATE NARANJOS SET dentro= ? WHERE numero_naranjo = ?"
            bd_cursor.execute(bd_query,(bd_dato_dentro,bd_dato_id))
            bd_conexion.commit()
            #-cambiamos el numero de operaciones
            bd_dato_numero_operaciones=naranjo_numero_operaciones[x]
            bd_dato_id=x


            bd_query="UPDATE NARANJOS SET numero_operaciones= ? WHERE numero_naranjo = ?"
            bd_cursor.execute(bd_query,(bd_dato_numero_operaciones,bd_dato_id))
            bd_conexion.commit()
            #-cambiamos el balance del naranjo
            bd_dato_balance=naranjo_balance[x]
            bd_dato_id=x


            bd_query="UPDATE NARANJOS SET balance= ? WHERE numero_naranjo = ?"
            bd_cursor.execute(bd_query,(bd_dato_balance,bd_dato_id))
            bd_conexion.commit()
           
            
            #-cambiamos la cantidad a comprar de BTC con el nuevo balance
           
            bd_dato_cantidad=naranjo_cantidad_comprar[x]
            bd_dato_id=x


            bd_query="UPDATE NARANJOS SET cantidad_comprar= ? WHERE numero_naranjo = ?"
            bd_cursor.execute(bd_query,(bd_dato_cantidad,bd_dato_id))
            bd_conexion.commit()
           
            bd_conexion.close()

   label_balance_total.config(text=balance_total)
   label_balance_porcentage.config(text=balance_porcentage_s)
   
   #----------lanzamos la funcion estadisticas para que las cambie cada minuto
   global minuto_anterior
   tiempo=datetime.now()
   hora=tiempo.time()
   minuto=hora.minute
   if minuto_anterior != minuto:
     estadisticas()
     #print('otro minuto')
   
   minuto_anterior=minuto

   #--------al final del dia metemos en la BD(diario) la informacion de como cerramos el dia
   # miramos si ha cambiado el dia para ver si arrancamos  
   global dia_anterior
   fecha=tiempo.date()
   dia=str(fecha)[8:10]
   #print(dia)
   #print(dia_anterior)
   if dia != dia_anterior:   # dia_anterior nos viene de la funcion diario_dia()
       bd_conexion=sqlite3.connect('naranjos')
       bd_cursor=bd_conexion.cursor()
       bd_fecha=fecha
       bd_deposito= cantidad_total   # nos viene de estadisticas
       bd_precio_btc= socket_precio
       bd_balance_total=pasta_total
       print(pasta_total)
       bd_conexion.execute( "INSERT INTO diario (fecha,deposito,precio_btc,balance_total) VALUES(?,?,?,?)",(bd_fecha,bd_deposito,bd_precio_btc,pasta_total))
       bd_conexion.commit()

       print('fecha:',fecha)
       dia_anterior= dia
       bd_conexion.close()


#***************************************************************************************************************
#*********************************************SOCKET************************************************************
#***************************************************************************************************************

# en shocket creamos un generador de eventos en segundo plano para que no pare el programa( y nos podamos meter en el bucle de la interfaz)
# nos mete en la funcion evento_f() que cada 3 segundos nos da el precio de la api 
# y lanzamos la funcion cada tick() para que mire lo que hay que hacer con el nuevo precio 
def mensage_socket(msg):
    #print( msg['c'])
    global socket_precio
    socket_precio =  msg['c']
    
    
    
    precio_texto=socket_precio[0:7]
       

    label_precio_socket.config(text=precio_texto)

    cada_tick()


def cambiar_label(self):
    self.config(text='texto3')

def evento_f():
    global client
    global socket_precio
    while True:
       time.sleep(3)
       datos=client.get_historical_trades(symbol='BTCUSDT',limit=10)
       datos_lista=datos[0]
       socket_precio=datos_lista['price']
    
       precio_texto=socket_precio[0:7]
       label_precio_socket.config(text=precio_texto)
       #print('entro')
       #print('p: ',socket_precio)
       #print(datos_lista)
       cada_tick()




def socket():
    #symbol='BTCUSDT'
    #twm=ThreadedWebsocketManager(api_key='SgLRNVSNnn8J1KMIjJeG0i4LBEMzcwcJfFpqJHgQHSQXRFjWMER1lySJ5LJHNOb2',api_secret='FtIR9C1xdTosRPDxtN7WCHZaMP7c9g114RHjpVHwmNfIsVfOawiXHoCoseOzv8lD')
    #twm.start()
    
    
    #datos=client.get_historical_trades(symbol='BTCUSDC',limit=10)
    #print(datos[0])
    #x=0
    #while(x==0):
    #   print('hola')
    #   time.sleep(2)
    #   datos=client.get_historical_trades(symbol='BTCUSDC',limit=10)
    #   print(datos[0])

    #twm.start_symbol_ticker_socket(callback=mensage_socket,symbol=symbol)
    
    
    evento_t=threading.Timer(3,evento_f) # el threading.timer crea un evento en segundo plano que no detiene la ejecucion del programa cuando lo metamos en un bucle infinito
    evento_t.start()              # rodamos el threding y lo enviamos a evento_f



#***************************************************************************************************************
#*********************************************INTERFAZ************************************************************
#***************************************************************************************************************



def interfaz():
    global balance_total

    raiz=Tk()  # creamos la raiz donde iran los frames
    raiz.title('Escudrinyator v0.1')
    #raiz.geometry('400x600')   3 hay que darle tamaño al frame ...no a la raiz, la raiz coge el tamaño de sus frames

    frame1=Frame()  # creamos el frame donde iran los witgets
    frame1.pack(side='left',anchor='n')   # lo empaquetamos dentro de la raiz, lo empaquetamos a la izquierda y con el anchor arriba
    frame1.config(width='350',height='550')
    frame1.config(bd='2')   # ancho del borde
    frame1.config(relief='groove')  # tipo de borde
    #frame1.grid(row=0, column=0, columnspan=2)

    frame2=Frame()  # creamos el frame donde iran los witgets
    frame2.pack(side='left',anchor='n')   # lo empaquetamos dentro de la raiz, lo empaquetamos a la izquierda y con el anchor arriba
    frame2.config(width='350',height='550')
    frame2.config(bd='2')   # ancho del borde
    frame2.config(relief='groove')  # tipo de borde
    #frame2.grid(row=1, column=0, columnspan=2)

    frame3=Frame()  # creamos el frame donde iran los witgets
    frame3.pack(side='left',anchor='n')   # lo empaquetamos dentro de la raiz, lo empaquetamos a la izquierda y con el anchor arriba
    frame3.config(width='350',height='550')
    frame3.config(bd='2')   # ancho del borde
    frame3.config(relief='groove')  # tipo de borde
    #frame2.grid(row=1, column=0, columnspan=2)

    frame4=Frame()  # creamos el frame donde iran los witgets
    frame4.pack(side='left',anchor='n')   # lo empaquetamos dentro de la raiz, lo empaquetamos a la izquierda y con el anchor arriba
    frame4.config(width='200',height='550')
    frame4.config(bd='2')   # ancho del borde
    frame4.config(relief='groove')  # tipo de borde
    #frame2.grid(row=1, column=0, columnspan=2)
    
    label_precio=Label(frame1,text='Precio: ',font=('Helvatical ',12))
    
    label_precio.grid(row=0,column=0,padx=10,pady=10)
    label_precio.place(x=10,y=10)

    global label_precio_socket
    label_precio_socket=Label(frame1,text=socket_precio,font=('Helvatical bold',12))
    label_precio_socket.grid(row=1,column=0,padx=10,pady=10)

    label_precio_socket.place(x=60,y=10)
       
    #---------------------campo de balance

    label_balance_total_t=Label(frame2,text='Balance: ',font=('Helvatical ',12))
    
    label_balance_total_t.grid(row=0,column=0,padx=10,pady=10)
    label_balance_total_t.place(x=10,y=10)

    global label_balance_total
    label_balance_total=Label(frame2,text=balance_total,font=('Helvatical bold',12))
    label_balance_total.grid(row=1,column=0,padx=10,pady=10)

    label_balance_total.place(x=70,y=10)
    
    #---------------------campo de balance porcentage

    
    label_balance_porcentage_t=Label(frame3,text='Balance Porcentage: ',font=('Helvatical ',12))
    
    label_balance_porcentage_t.grid(row=0,column=0,padx=10,pady=10)
    label_balance_porcentage_t.place(x=10,y=10)

    global label_balance_porcentage
    label_balance_porcentage=Label(frame3,text=balance_total,font=('Helvatical bold',12))
    label_balance_porcentage.grid(row=1,column=0,padx=10,pady=10)

    label_balance_porcentage.place(x=170,y=10)

    
    #**********************************************naranjos****************************************************
    global label_naranjo0_entrada;global label_naranjo1_entrada;global label_naranjo2_entrada;global label_naranjo3_entrada;global label_naranjo4_entrada;global label_naranjo5_entrada;global label_naranjo6_entrada;global label_naranjo7_entrada;global label_naranjo8_entrada;global label_naranjo9_entrada;global label_naranjo10_entrada;global label_naranjo11_entrada;global label_naranjo12_entrada;global label_naranjo13_entrada;global label_naranjo14_entrada;global label_naranjo15_entrada;global label_naranjo16_entrada;global label_naranjo17_entrada;global label_naranjo18_entrada;global label_naranjo19_entrada;global label_naranjo20_entrada;global label_naranjo21_entrada;global label_naranjo22_entrada;global label_naranjo23_entrada;global label_naranjo24_entrada;global label_naranjo25_entrada;global label_naranjo26_entrada;global label_naranjo27_entrada;global label_naranjo28_entrada;global label_naranjo29_entrada;global label_naranjo30_entrada;global label_naranjo31_entrada;global label_naranjo32_entrada;global label_naranjo33_entrada;global label_naranjo34_entrada;global label_naranjo35_entrada;global label_naranjo36_entrada;global label_naranjo37_entrada;global label_naranjo38_entrada;global label_naranjo39_entrada;global label_naranjo40_entrada;global label_naranjo41_entrada;global label_naranjo42_entrada;global label_naranjo43_entrada;global label_naranjo44_entrada;global label_naranjo45_entrada;global label_naranjo46_entrada;global label_naranjo47_entrada;global label_naranjo48_entrada;global label_naranjo49_entrada;global label_naranjo50_entrada;global label_naranjo51_entrada;global label_naranjo52_entrada;global label_naranjo53_entrada;global label_naranjo54_entrada;global label_naranjo55_entrada;global label_naranjo56_entrada;global label_naranjo57_entrada;global label_naranjo58_entrada;global label_naranjo59_entrada;global label_naranjo60_entrada;global label_naranjo61_entrada;global label_naranjo62_entrada;global label_naranjo63_entrada;global label_naranjo64_entrada;global label_naranjo65_entrada;global label_naranjo66_entrada;global label_naranjo67_entrada;global label_naranjo68_entrada;global label_naranjo69_entrada;global label_naranjo70_entrada;global label_naranjo71_entrada;global label_naranjo72_entrada;global label_naranjo73_entrada;global label_naranjo74_entrada;global label_naranjo75_entrada;global label_naranjo76_entrada;global label_naranjo77_entrada;global label_naranjo78_entrada;global label_naranjo79_entrada;global label_naranjo80_entrada;global label_naranjo81_entrada;global label_naranjo82_entrada;global label_naranjo83_entrada;global label_naranjo84_entrada;global label_naranjo85_entrada;global label_naranjo86_entrada;global label_naranjo87_entrada;global label_naranjo88_entrada;global label_naranjo89_entrada;global label_naranjo90_entrada;global label_naranjo91_entrada;global label_naranjo92_entrada;global label_naranjo93_entrada;global label_naranjo94_entrada;global label_naranjo95_entrada;global label_naranjo96_entrada;global label_naranjo97_entrada;global label_naranjo98_entrada;global label_naranjo99_entrada
    
    #label_naranjo0=Label(frame1,text='Naranjo0: ',font=('Helvatical bold',8))
    #label_naranjo0.place(x=10,y=30)

    #label_naranjo1=Label(frame1,text='Naranjo1: ',font=('Helvatical bold',8))
    #label_naranjo1.place(x=10,y=45)
    
    #label_naranjo2=Label(frame1,text='Naranjo2: ',font=('Helvatical bold',8))
    #label_naranjo2.place(x=10,y=60)

    #label_naranjo3=Label(frame1,text='Naranjo3: ',font=('Helvatical bold',8))
    #label_naranjo3.place(x=10,y=75)
   
    #label_naranjo4=Label(frame1,text='Naranjo4: ',font=('Helvatical bold',8))
    #label_naranjo4.place(x=10,y=90)
   
    #label_naranjo5=Label(frame1,text='Naranjo5: ',font=('Helvatical bold',8))
    #label_naranjo5.place(x=10,y=105)
   
    #label_naranjo6=Label(frame1,text='Naranjo6: ',font=('Helvatical bold',8))
    #label_naranjo6.place(x=10,y=120)

    #label_naranjo7=Label(frame1,text='Naranjo7: ',font=('Helvatical bold',8))
    #label_naranjo7.place(x=10,y=135)

    #label_naranjo8=Label(frame1,text='Naranjo8: ',font=('Helvatical bold',8))
    #label_naranjo8.place(x=10,y=150)

    #label_naranjo9=Label(frame1,text='Naranjo9: ',font=('Helvatical bold',8))
    #label_naranjo9.place(x=10,y=165)

    #label_naranjo10=Label(frame1,text='Naranjo10: ',font=('Helvatical bold',8))
    #label_naranjo10.place(x=10,y=180)

    #label_naranjo11=Label(frame1,text='Naranjo11: ',font=('Helvatical bold',8))
    #label_naranjo11.place(x=10,y=195)

    #label_naranjo12=Label(frame1,text='Naranjo12: ',font=('Helvatical bold',8))
    #label_naranjo12.place(x=10,y=210)

    #label_naranjo13=Label(frame1,text='Naranjo13: ',font=('Helvatical bold',8))
    #label_naranjo13.place(x=10,y=225)

    #label_naranjo14=Label(frame1,text='Naranjo14: ',font=('Helvatical bold',8))
    #label_naranjo14.place(x=10,y=240)

    #label_naranjo15=Label(frame1,text='Naranjo15: ',font=('Helvatical bold',8))
    #label_naranjo15.place(x=10,y=255)

    #label_naranjo16=Label(frame1,text='Naranjo16: ',font=('Helvatical bold',8))
    #label_naranjo16.place(x=10,y=270)

    #label_naranjo17=Label(frame1,text='Naranjo17: ',font=('Helvatical bold',8))
    #label_naranjo17.place(x=10,y=285)
    
    #az=0
    
    #text='Naranjo'+ str(18) + ': '
    #prueva.insert(az,Label(frame1,text=text,font=('Helvatical bold',8)))
    #prueva[0]=Label(frame1,text='Naranjo18: ',font=('Helvatical bold',8))
    #prueva[az].place(x=10,y=300)

    
    #----------Creamos un bucle para hacer una lista de labels: la que va a llevar el nombre del naranjo  
    linea=0  # para el nombre del primer naranjo
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    for x in range(33):
       
       text='Naranjo'+ str(linea) + ': '  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       prueva.insert(x,Label(frame1,text=text,font=('Helvatical bold',8)))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       prueva[x].place(x=10,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15
       
    
    linea=33  # para el nombre del primer naranjo del 2º frame
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    for x in range(33,66):
       
       text='Naranjo'+ str(linea) + ': '  
       prueva.insert(x,Label(frame2,text=text,font=('Helvatical bold',8)))   
       prueva[x].place(x=10,y=linea_y)    
       linea= linea +1
       linea_y= linea_y + 15

    linea=66  # para el nombre del primer naranjo del 3º frame
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    for x in range(66,100):
       
       text='Naranjo'+ str(linea) + ': '  
       prueva.insert(x,Label(frame3,text=text,font=('Helvatical bold',8)))   
       prueva[x].place(x=10,y=linea_y)    
       linea= linea +1
       linea_y= linea_y + 15
   
    #-----------------------------------------labels del precio de entrada---------------------------------- 

    #linea=0  # para el nombre del primer naranjo
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=70
    for x in range(33):
       
       text=naranjos_precio_entrada[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_precio_entrada.insert(x,Label(frame1,text=text,font=('Helvatical bold',8),fg='#595a5b'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_precio_entrada[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

   
    linea=0  # para el nombre del primer naranjo
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=70
    for x in range(33,66):
       
       text=naranjos_precio_entrada[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_precio_entrada.insert(x,Label(frame2,text=text,font=('Helvatical bold',8),fg='#595a5b'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_precio_entrada[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15
   
   
    
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=70
    for x in range(66,100):
       
       text=naranjos_precio_entrada[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_precio_entrada.insert(x,Label(frame3,text=text,font=('Helvatical bold',8),fg='#595a5b'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_precio_entrada[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15
   
    
    #-----------------------------------------labels del precio de salida---------------------------------- 

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=120
    for x in range(33):
       
       text=naranjo_take[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_precio_take.insert(x,Label(frame1,text=text,font=('Helvatical bold',8),fg='#7b8e98'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_precio_take[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15
    
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=120
    for x in range(33,66):
       
       text=naranjo_take[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_precio_take.insert(x,Label(frame2,text=text,font=('Helvatical bold',8),fg='#7b8e98'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_precio_take[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15
    
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=120
    for x in range(66,100):
       
       text=naranjo_take[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_precio_take.insert(x,Label(frame3,text=text,font=('Helvatical bold',8),fg='#7b8e98'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_precio_take[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15


      #-----------------------------------------labels dentro/Fuera---------------------------------- 

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=170
    for x in range(33):    #si es true le decimos que saque la letra D y sea verde y si es falso la letra F y rojo
       if naranjo_dentro[x]:  
         text='D'  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
         text_color='#50ee58'
       else:
         text='F'
         text_color='#f5888e'

       label_naranjo_dentro.insert(x,Label(frame1,text=text,font=('Helvatical bold',8),fg=text_color))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_dentro[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15
       

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=170
    for x in range(33,66):    #si es true le decimos que saque la letra D y sea verde y si es falso la letra F y rojo
       if naranjo_dentro[x]:  
         text='D'  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
         text_color='#50ee58'
       else:
         text='F'
         text_color='#f5888e'

       label_naranjo_dentro.insert(x,Label(frame2,text=text,font=('Helvatical bold',8),fg=text_color))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_dentro[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15
    
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=170
    for x in range(66,100):    #si es true le decimos que saque la letra D y sea verde y si es falso la letra F y rojo
       if naranjo_dentro[x]:  
         text='D'  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
         text_color='#50ee58'
       else:
         text='F'
         text_color='#f5888e'

       label_naranjo_dentro.insert(x,Label(frame3,text=text,font=('Helvatical bold',8),fg=text_color))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_dentro[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

     #-----------------------------------------labels numero de operaciones---------------------------------- 

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=180
    for x in range(33):
       
       text=naranjo_numero_operaciones[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_naranjo_numero_operaciones.insert(x,Label(frame1,text=text,font=('Helvatical bold',8),fg='#0c0c0c'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_numero_operaciones[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=180
    for x in range(33,66):
       
       text=naranjo_numero_operaciones[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_naranjo_numero_operaciones.insert(x,Label(frame2,text=text,font=('Helvatical bold',8),fg='#0c0c0c'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_numero_operaciones[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

    
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=180
    for x in range(66,100):
       
       text=naranjo_numero_operaciones[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_naranjo_numero_operaciones.insert(x,Label(frame3,text=text,font=('Helvatical bold',8),fg='#0c0c0c'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_numero_operaciones[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

      #-----------------------------------------labels balance de cada naranjo---------------------------------- 

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=200
    for x in range(33):
       
       text=naranjo_balance[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_naranjo_balance.insert(x,Label(frame1,text=text,font=('Helvatical bold',8),fg='#319d75'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_balance[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=200
    for x in range(33,66):
       
       text=naranjo_balance[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_naranjo_balance.insert(x,Label(frame2,text=text,font=('Helvatical bold',8),fg='#319d75'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_balance[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=200
    for x in range(66,100):
       
       text=naranjo_balance[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_naranjo_balance.insert(x,Label(frame3,text=text,font=('Helvatical bold',8),fg='#319d75'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_balance[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

     #-----------------------------------------labels porcentage ganadora o perdedora de la entrada---------------------------------- 

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=240
    for x in range(33):
       
       text=naranjo_porcentage_balance[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_porcentage_balance.insert(x,Label(frame1,text=text,font=('Helvatical bold',8),fg='#e4c704'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_porcentage_balance[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15
    
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=240
    for x in range(33,66):
       text=naranjo_porcentage_balance[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_porcentage_balance.insert(x,Label(frame2,text=text,font=('Helvatical bold',8),fg='#e4c704'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_porcentage_balance[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=240
    for x in range(66,100):
       text=naranjo_porcentage_balance[x]  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_porcentage_balance.insert(x,Label(frame3,text=text,font=('Helvatical bold',8),fg='#e4c704'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_porcentage_balance[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

     #-----------------------------------------labels donde est el precio---------------------------------- 

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=270
    for x in range(33):
       
       text=""  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_naranjo_en_precio.insert(x,Label(frame1,text=text,font=('Helvatical bold',8),fg='#e109c5'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_en_precio[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15
    
    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=270
    for x in range(33,66):
       text=''  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_naranjo_en_precio.insert(x,Label(frame2,text=text,font=('Helvatical bold',8),fg='#e109c5'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_en_precio[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

    linea_y= 30 # pixel donde empiezamos a meter label en el eje y
    linea_x=270
    for x in range(66,100):
       text=''  # texto de la lavel: naranjo mas el numero que nos da la x del bucle
       label_naranjo_en_precio.insert(x,Label(frame3,text=text,font=('Helvatical bold',8),fg='#e109c5'))   # creamos un nuevo elemento de la lista con el metodo .apend...en el x le damos la posicion de la lista
       label_naranjo_en_precio[x].place(x=linea_x,y=linea_y)    # empaquetamos la label y la colocamos en su sitio
       linea= linea +1
       linea_y= linea_y + 15

   
    #-------------FRAME DE DATOS------------------------------------
       
    #------------------------------------labels------------------------------
    #-------------deposito
    label_deposito=Label(frame4,text='Deposito: ',font=('Helvatical ',9))
    
    label_deposito.grid(row=0,column=0,padx=10,pady=10)
    label_deposito.place(x=10,y=10)

    global label_deposito_var
    label_deposito_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',9))
    label_deposito_var.grid(row=1,column=0,padx=10,pady=10)

    label_deposito_var.place(x=75,y=10)
    #---------------balance total

    #btc
    label_btc=Label(frame4,text='BTC: ',font=('Helvatical ',9))
    label_btc.place(x=10,y=30)

    global label_btc_var
    label_btc_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',9))
    label_btc_var.place(x=75,y=30)
    #btc en usdt  
    label_btc_en_usdt=Label(frame4,text='btc en usdt: ',font=('Helvatical ',8))
    label_btc_en_usdt.place(x=10,y=45)

    global label_btc_en_usdt_var
    label_btc_en_usdt_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',8))
    label_btc_en_usdt_var.place(x=75,y=45)

    #bnb
    label_bnb=Label(frame4,text='BNB: ',font=('Helvatical ',9))
    label_bnb.place(x=10,y=70)

    global label_bnb_var
    label_bnb_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',9))
    label_bnb_var.place(x=75,y=70)
    
    #bnb en usdt
    label_bnb_en_usdt=Label(frame4,text='bnb en usdt: ',font=('Helvatical ',8))
    label_bnb_en_usdt.place(x=10,y=85)

    global label_bnb_en_usdt_var
    label_bnb_en_usdt_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',8))
    label_bnb_en_usdt_var.place(x=75,y=85)
    
    #usdt
    label_usdt=Label(frame4,text='USDT: ',font=('Helvatical ',9))
    label_usdt.place(x=10,y=110)

    global label_usdt_var
    label_usdt_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',9))
    label_usdt_var.place(x=75,y=110)
    
    #Total

    label_total=Label(frame4,text='Total: ',font=('Helvatical ',9))
    label_total.place(x=10,y=130)

    global label_total_var
    label_total_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',9))
    label_total_var.place(x=75,y=130)

    #Balance
        
    label_balance=Label(frame4,text='Balance: ',font=('Helvatical ',9))
    label_balance.place(x=10,y=145)

    global label_balance_var
    label_balance_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',9))
    label_balance_var.place(x=75,y=145)

    #separador
    label_separador=Label(frame4,text='--------------------------------------- ',font=('Helvatical ',9))
    label_separador.place(x=10,y=160)
    
    #tiempo
    label_hora=Label(frame4,text='Time: ',font=('Helvatical ',9))
    label_hora.place(x=10,y=175)

    global label_hora_var
    label_hora_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',9))
    label_hora_var.place(x=75,y=175)
    

    #Balance maximo    
    label_balance_maximo=Label(frame4,text='Bal. max.: ',font=('Helvatical ',9))
    label_balance_maximo.place(x=10,y=190)

    global label_balance_maximo_var
    label_balance_maximo_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',9))
    label_balance_maximo_var.place(x=75,y=190)

    #Balance maximo dia
    label_balance_maximo_dia=Label(frame4,text='Bal. Max. dia: ',font=('Helvatical ',8))
    label_balance_maximo_dia.place(x=10,y=205)

    global label_balance_maximo_dia_var
    label_balance_maximo_dia_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',8))
    label_balance_maximo_dia_var.place(x=75,y=205)

    #Balance minimo    
    label_balance_minimo=Label(frame4,text='Bal. min.: ',font=('Helvatical ',9))
    label_balance_minimo.place(x=10,y=225)

    global label_balance_minimo_var
    label_balance_minimo_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',9))
    label_balance_minimo_var.place(x=75,y=225)

    #Balance maximo dia
    label_balance_minimo_dia=Label(frame4,text='Bal. min. dia: ',font=('Helvatical ',8))
    label_balance_minimo_dia.place(x=10,y=240)

    global label_balance_minimo_dia_var
    label_balance_minimo_dia_var=Label(frame4,text='mucha pasta',font=('Helvatical bold',8))
    label_balance_minimo_dia_var.place(x=75,y=240)





    
    #estadisticas() # para que cambie las labels de estadisticas
    raiz.mainloop()




#***************************************************************************************************************
#*********************************************CREAMOS LOS PARAMETROS DE CADA NARANJO************************************************************
#***************************************************************************************************************

def crea_naranjos():  # vamos a crear listas con los precios de entrada, take profit, balance....de cada naranjo
    rango_total_particion=rango_mayor - rango_menor   # para ver lo grande que va a ser la particion total
    rango_pequeño_particion= rango_total_particion / naranjos_numero
    linea_print= str(rango_total_particion) + ' -- ' + str(rango_pequeño_particion) 
   
    #----------------------------vamos a por los precios de entrada de cada naranjo-------------------
    particiones_suma= rango_menor # aqui va el precio de entrada de cada naranjo

    
    for x in range(100):
       
       naranjos_precio_entrada[x]= particiones_suma    
       naranjo_take[x]= naranjos_precio_entrada[x] * (1 + (take / 100))
       naranjo_dentro[x]=False
       naranjo_numero_operaciones[x]=0 
       naranjo_balance[x]= 20
       # sacamos el porcenaje que ha subido o bajado la orden
       
       naranjo_porcentage_balance[x]=balance_inicial
       naranjo_cantidad_comprar[x]= naranjo_balance[x]/ naranjos_precio_entrada[x] # cuanto btc hay que comprar según el balance de cada naranjo 
       

       particiones_suma=particiones_suma + rango_pequeño_particion   # le sumamos el espaciio entre particion para que a la siguiente vuelta meter el precio de entrada
       
#***************************************************************************************************************
#*********************************************METEMOS LOS PARAMETROS DE CADA NARANJO DESDE LA DB************************************************************
#***************************************************************************************************************


def crea_naranjos_desde_bd():  # vamos a llenar los parametros de cada naranjo desde la bd

   
   bd_conexion=sqlite3.connect("naranjos")
   bd_cursor=bd_conexion.cursor()
   
   for x in range(100):
      bd_query="SELECT * FROM NARANJOS WHERE numero_naranjo = ? "
      bd_cursor.execute(bd_query,(x,))
      bd_datos= bd_cursor.fetchall()
      bd_datos=bd_datos[0]     # nos da una lista y nosotros la convertimos en tupla para extraer los datos de uno en uno   
   
      numero_naranjo=bd_datos[0]   
      #naranjos_numero[x]= numero_naranjo
      naranjos_precio_entrada[x]=bd_datos[1]
      naranjo_take[x]=bd_datos[2]
      naranjo_dentro[x]=bd_datos[3]
      naranjo_numero_operaciones[x]=bd_datos[4]
      naranjo_balance[x]=bd_datos[5]
      naranjo_porcentage_balance[x]=bd_datos[6]
      naranjo_cantidad_comprar[x]=bd_datos[7]

   bd_conexion.close()

#***************************************************************************************************************
#*********************************************ESTADISTICAS************************************************************
#***************************************************************************************************************
#entra despues de crear el interfaz y cada minuto en cada_tick


def estadisticas():

    #------------------------------Depositos--------------------------------------------------------
    global cantidad_total
    global label_deposito_var
    bd_conexion=sqlite3.connect('naranjos')
    bd_cursor=bd_conexion.cursor()   
    cantidad_total=0

    bd_query=" SELECT * FROM depositos"
    bd_cursor.execute(bd_query)
    bd_salida=bd_cursor.fetchall()

    for x in bd_salida:                                # sumamos todas las cantidades de la bd de depositos para meterlo en su label
      cantidad_total=cantidad_total + x[1]    
    label_deposito_var.config(text=cantidad_total)
    
    bd_conexion.close()

    #----------------------------Balance--------------------------------------------------------------------
    #BTC
    global socket_precio
    datos=client.get_historical_trades(symbol='BTCUSDT',limit=10)
    datos_lista=datos[0]
    socket_precio=datos_lista['price']
    precio_texto=socket_precio[0:7]
    
    
    cantidad_btc=client.get_asset_balance(asset='BTC')
    cantidad_btc=cantidad_btc['free'][0:7]
    #print('Cantidad BTC: ',cantidad_btc[0:7])
    pasta_en_btc=float(socket_precio) * float(cantidad_btc)
    #print('precio:',socket_precio)
    pasta_en_btc=str(pasta_en_btc)[0:7] #  crack...pasamos pasta_en_btc a srting,era float para poder coger los 7 primeros caracteres
    label_btc_var.config(text=cantidad_btc)
    label_btc_en_usdt_var.config(text=pasta_en_btc)
 
    #BNB

    datos=client.get_historical_trades(symbol='BNBUSDT',limit=10)
    datos_lista=datos[0]
    socket_precio_bnb=datos_lista['price']
    precio_texto_bnb=socket_precio_bnb[0:7]
    
    cantidad_bnb=client.get_asset_balance(asset='BNB')
    cantidad_bnb=cantidad_bnb['free'][0:7]
    #print('Cantidad BNB: ',cantidad_bnb[0:7])
    label_bnb_var.config(text=cantidad_bnb)
    
    pasta_en_usdt=float(socket_precio_bnb) * float(cantidad_bnb)
    pasta_en_usdt=str(pasta_en_usdt)[0:7]
    label_bnb_en_usdt_var.config(text=pasta_en_usdt)

    #USDT
    cantidad_usdt=client.get_asset_balance(asset='USDT')
    cantidad_usdt=cantidad_usdt['free'][0:7]
    label_usdt_var.config(text=cantidad_usdt)
    
    #TOTAL
    global pasta_total # lo usaremos cuando guardemos las estadisticas diarias en cada_click()
    pasta_total=float(pasta_en_btc) + float(pasta_en_usdt) + float(cantidad_usdt)
    label_total_var.config(text=str(pasta_total)[0:7])

    #Balance

    balance= pasta_total - cantidad_total # pasta total es la suma de las cripto que tengo y cantidad total la suma de los depositos que he hecho
    label_balance_var.config(text=str(balance)[0:7])
   
    if balance> 0 :                         # si es positivo de color vrede y si es negativo lo ponemos en rojo
        label_balance_var.config(fg='#22b486')
    else:
         label_balance_var.config(fg='#f5888e')

    #hora
    tiempo=datetime.now()
    fecha=tiempo.date()
    hora=tiempo.time()
    minuto=hora.minute
    hora=str(hora)[0:8]
    
    label_hora_var.config(text=hora)

   #balance máximo   #vamos a abrir la base de datos y recuperar el balance maximo que tenemos guardao en la db
    
    bd_conexion=sqlite3.connect('naranjos')
    bd_cursor=bd_conexion.cursor()   
    
    bd_query=" SELECT * FROM cosas"       #sacamos todos los datos ( maximo y minimo, por ahora no hay nada mas)
    bd_cursor.execute(bd_query)           #y lo metemos en bd_salida, una lista con los datos que nos hacen falta           
    bd_salida=bd_cursor.fetchall()

    bd_conexion.close()      # cierro ya la bd xq tengo los datos ya en bd_salida
    
    #print(bd_salida)
    
    balance_minimo_tupla= bd_salida[0]    # en la primera tupla tengo el balance minimo
    
    balance_minimo_cantidad=balance_minimo_tupla[2] # la lista la convertimos en tupla y de ahi sacamos el balance minimo
    balance_minimo_fecha=balance_minimo_tupla[0]
    label_balance_minimo_var.config(text=balance_minimo_cantidad)
    label_balance_minimo_dia_var.config(text=balance_minimo_fecha)
    
    balance_maximo_tupla= bd_salida[1]     # en la segunda tupla tengo el balance maximo
    
    balance_maximo_cantidad=balance_maximo_tupla[2] # la lista la convertimos en tupla y de ahi sacamos el balance minimo
    balance_maximo_fecha=balance_maximo_tupla[0]
    label_balance_maximo_var.config(text=balance_maximo_cantidad)
    label_balance_maximo_dia_var.config(text=balance_maximo_fecha)

    #cambiamos bal max o min si hiciera falta

    if balance > balance_maximo_cantidad:   # si el nuevo balance es superior al antiguo
       bd_conexion=sqlite3.connect('naranjos')  # el dato se vera en el siguiente minuto...no ahora
       bd_cursor=bd_conexion.cursor()   
       
       query_cantidad=str(balance)[0:7]  #primero cambiamos el balance
       query_descripcion='balance maximo'
       bd_query="UPDATE cosas SET cantidad= ? WHERE descripcion = ?"
       bd_cursor.execute(bd_query,(query_cantidad,query_descripcion))
       bd_conexion.commit()       
       
       query_fecha=fecha  #despues cambiamos la fecha
       query_descripcion='balance maximo'
       bd_query="UPDATE cosas SET fecha= ? WHERE descripcion = ?"
       bd_cursor.execute(bd_query,(query_fecha,query_descripcion))
       bd_conexion.commit()     

       bd_conexion.close()

    if balance < balance_minimo_cantidad:   # si el nuevo balance es inferior al antiguo
       print('entro')
       
       bd_conexion=sqlite3.connect('naranjos')  # el dato se vera en el siguiente minuto...no ahora
       bd_cursor=bd_conexion.cursor()   
       
       query_cantidad=str(balance)[0:7]  #primero cambiamos el balance
       query_descripcion='balance minimo'
       bd_query="UPDATE cosas SET cantidad= ? WHERE descripcion = ?"
       bd_cursor.execute(bd_query,(query_cantidad,query_descripcion))
       bd_conexion.commit()       
       
       query_fecha=fecha  #despues cambiamos la fecha
       query_descripcion='balance minimo'
       bd_query="UPDATE cosas SET fecha= ? WHERE descripcion = ?"
       bd_cursor.execute(bd_query,(query_fecha,query_descripcion))
       bd_conexion.commit()     

       bd_conexion.close()

def diario_dia():  # sacamos el dia de la ultima vez que metimos las estadisticas diarias
    global dia_anterior
    bd_conexion=sqlite3.connect('naranjos')
    bd_cursor=bd_conexion.cursor()

    bd_query=" SELECT * FROM diario"
    bd_cursor.execute(bd_query)
    bd_salida=bd_cursor.fetchall()

                       #sacamos la cantidad de registros que hay en la BD
    bd_numero_registros=len(bd_salida)
    bd_ultimo_registro= bd_salida[bd_numero_registros-1]   # sacamos los datos del ultimo registro
   
    fecha=bd_ultimo_registro[1]
    dia_anterior= fecha[8:10]
   




#***************************************************************************************************************
#*********************************************MAIN************************************************************
#***************************************************************************************************************
def main():
    
    
    diario_dia()
    socket()
    
    if bd_llena==False:       # si la Bd no esta llena creamos la informacion de los naranjos por primera vez
       crea_naranjos()
       print('entra por crea naranjos')                 
       db()  

    if bd_llena==True:             # si la base de BD esta llena enviamos los datos de los naranjos desde la BD
       print("entra por db")
       crea_naranjos_desde_bd()    
    
    if bd_llena==False:   # si la base de datos ya esta llena no la creamos y vamos a meter los datos de la BD en los naranjos
       db()               # si esta vacia porque es la primera vez que entramos la crearemos
       
    
    interfaz()
    
    
    #-------------------------provando cositas--------------------------------------------
    #bd_conexion=sqlite3.connect('naranjos')
    #bd_cursor=bd_conexion.cursor()
    #bd_dato_precio=123
    #bd_dato_id=0


    #bd_query="UPDATE NARANJOS SET precio_entrada= ? WHERE numero_naranjo = ?"
    #bd_cursor.execute(bd_query,(bd_dato_precio,bd_dato_id))
    #bd_conexion.commit()



    #bd_conexion.close()

    print('fin main')


if __name__ == "__main__":
    main()
    