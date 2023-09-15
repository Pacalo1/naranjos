#diario_v_0.01   epezamos con esto
import tkinter
from tkinter import *
import sqlite3
import time

def conexion_db():
    global bd_datos
    global datos_len
    bd_conexion=sqlite3.connect('naranjos')
    bd_cursor=bd_conexion.cursor()

    bd_query="SELECT * FROM diario"
    bd_cursor.execute(bd_query)
    bd_datos= bd_cursor.fetchall()

    #print(bd_datos)
    datos_len=len(bd_datos)
    #print(datos_len)

def interfaz():
    
    balance_anterior=1   # variable donde meteremos el balance del dia anterior
    mes_actual=13 # variable para sacar el porcentege mensual
    precio_btc_anterior =1 #  metermos el precio del btc del dia anterior
    
    raiz=Tk()
    raiz.title('escudriñator_diario')
    
    
    frame1=Frame()  # creamos el frame donde iran los witgets
    frame1.pack(side='left',anchor='n')   # lo empaquetamos dentro de la raiz, lo empaquetamos a la izquierda y con el anchor arriba
    frame1.config(width='600',height='700')
    frame1.config(bd='2')   # ancho del borde
    frame1.config(relief='groove')  # tipo de borde
    
    label_titulo=Label(frame1,text='Diario ',font=('Helvatical ',12))    
    label_titulo.grid(row=0,column=0,padx=10,pady=10)
    label_titulo.place(x=10,y=5)
    
    #------------labels etiquetas columnas--------------------------------------------

    label_titulo_numero=Label(frame1,text='Numero ',font=('Helvatical ',8))    
    label_titulo_numero.place(x=10,y=25)
    label_titulo_fecha=Label(frame1,text='Fecha ',font=('Helvatical ',8))    
    label_titulo_fecha.place(x=60,y=25)
    label_titulo_deposito=Label(frame1,text='Deposito ',font=('Helvatical ',8))    
    label_titulo_deposito.place(x=110,y=25)
    label_titulo_precio=Label(frame1,text='Precio_btc ',font=('Helvatical ',8))    
    label_titulo_precio.place(x=170,y=25)
    label_titulo_balance=Label(frame1,text='Balance ',font=('Helvatical ',8))    
    label_titulo_balance.place(x=230,y=25)
    label_titulo_gp=Label(frame1,text='Gan/Perd ',font=('Helvatical ',8))    
    label_titulo_gp.place(x=280,y=25)
    label_titulo_por_gp=Label(frame1,text='"%" Gan ',font=('Helvatical ',8))    
    label_titulo_por_gp.place(x=340,y=25)
    label_titulo_por_diario=Label(frame1,text='"%"diario ',font=('Helvatical ',8))    
    label_titulo_por_diario.place(x=395,y=25)
    label_titulo_por_mes=Label(frame1,text='"%"del mes ',font=('Helvatical ',8))    
    label_titulo_por_mes.place(x=455,y=25)
    label_titulo_por_btc=Label(frame1,text='"%" btc ',font=('Helvatical ',8))    
    label_titulo_por_btc.place(x=525,y=25)

    #---------------------campos de datos--------------------------------------------------
    linea_y=40
    label_numero=[1]   #creamos la lista de la label del numero
    label_fecha=[1]
    label_deposito=[1]
    label_precio_btc=[1]
    label_balance_total=[1]
    label_ganancia=[1]
    label_por_ganancia=[1]
    label_por_diario=[1]
    label_por_mes=[1]
    label_por_btc=[1]

    for x in range(0,datos_len): # vamos mirando dia por dia

        registro=bd_datos[x]  #sacamos la tupla del registro del numero de lista 
        numero=registro[0]
        fecha=registro[1]
        deposito=registro[2]
        precio_btc=registro[3]
        balance_total=registro[4]
        balance_total=str(balance_total)[0:6]


        #---------datos que viene de la BD---------------------------
        label_numero.insert(x,Label(frame1,text=numero,font=('Helvatical bold',8)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_numero[x].place(x=10,y=linea_y)
         
        label_fecha.insert(x,Label(frame1,text=fecha,font=('Helvatical bold',7)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_fecha[x].place(x=55,y=linea_y)
        
        label_deposito.insert(x,Label(frame1,text=deposito,font=('Helvatical bold',7)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_deposito[x].place(x=115,y=linea_y)

        label_precio_btc.insert(x,Label(frame1,text=precio_btc,font=('Helvatical bold',7)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_precio_btc[x].place(x=175,y=linea_y)

        label_balance_total.insert(x,Label(frame1,text=balance_total,font=('Helvatical bold',7)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_balance_total[x].place(x=235,y=linea_y)
        #-------------datos que calculamos -------------------------
        #----------ganacia-------------------------------------
        ganancia= float(balance_total)- deposito
        ganancia=str(ganancia)[0:5]
        label_ganancia.insert(x,Label(frame1,text=ganancia,font=('Helvatical bold',7)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_ganancia[x].place(x=285,y=linea_y)
        if float(ganancia) > 0 :
            label_ganancia[x].config(fg='#22b486')
        else:
            label_ganancia[x].config(fg='#f5888e')

        #--------porcentage ganancia-----------------------------
        por_ganancia= (float(ganancia) *100)/deposito
        por_ganancia=str(por_ganancia)[0:4]
        label_por_ganancia.insert(x,Label(frame1,text=por_ganancia,font=('Helvatical bold',7)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_por_ganancia[x].place(x=345,y=linea_y)
        if float(por_ganancia) > 0 :
            label_por_ganancia[x].config(fg='#22b486')
        else:
            label_por_ganancia[x].config(fg='#f5888e')
        
        #---------porcentage diario-----------------
        
        
        por_diario= float(balance_total)/float(balance_anterior) # balance_anterior nos viane de un campo que cree cuando leiamos el registro anterior y me lo guardo para tener este dato del dia de antes 
        por_diario=por_diario -1
        por_diario=por_diario * 100
        por_diario=str(por_diario)[0:4]
        
        
        label_por_diario.insert(x,Label(frame1,text=por_diario,font=('Helvatical bold',7)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_por_diario[x].place(x=400,y=linea_y)
        if float(por_diario) > 0 :
            label_por_diario[x].config(fg='#22b486')
        else:
            label_por_diario[x].config(fg='#f5888e')
        
        #--------porcentage del mes----------------------------------
        
        #      tenenmos que sacar el balance del primer dia del mes(del mes en que estemos) que tenemos registrado...deberia ser el dia 1, pero por si no tenemos egistro del dia 1
       
        dia=fecha[8:10]
        
        mes=fecha[5:7]
        
        
        if mes != mes_actual:   # si cambia el mes es que es el primer dia del mes...cogemos el valor de balance total de ese dia para compararlo con los dias del mismo mes
           
            balance_total_dia_1=balance_total
            mes_actual=mes # lo cambiamos para que no entre mas hast que cambiemos de mes
        
        
        por_mes=float(balance_total)/float(balance_total_dia_1)
        por_mes=por_mes-1
        por_mes=por_mes*100
        por_mes=str(por_mes)[0:4]
        label_por_mes.insert(x,Label(frame1,text=por_mes,font=('Helvatical bold',7)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_por_mes[x].place(x=465,y=linea_y)
        if float(por_mes) > 0 :
            label_por_mes[x].config(fg='#22b486')
        else:
            label_por_mes[x].config(fg='#f5888e')

        

        #------porcentage btc------------------
        # vamos a ver el porcentage que sube o baja el btc por dia
        por_btc=float(precio_btc)/float(precio_btc_anterior)
        print('precio btc anterior: ',precio_btc_anterior)
        print('precio btc: ',precio_btc)
        print('porcentage:', por_btc)
        por_btc=por_btc -1
        por_btc=por_btc*100
        por_btc=str(por_btc)[0:4] 
        label_por_btc.insert(x,Label(frame1,text=por_btc,font=('Helvatical bold',7)))  # insertamos una nueva label en la lista, con numero x, se crea una lavel en el frame 1...
        label_por_btc[x].place(x=530,y=linea_y)
        if float(por_btc) > 0 :
            label_por_btc[x].config(fg='#22b486')
        else:
            label_por_btc[x].config(fg='#f5888e')
        
        print('------------------------------')


 



        
        balance_anterior=balance_total #esto lo usaremos cuando lea el siguiente registro para saber el balance del dia de antes 
        linea_y=linea_y +15 # le sumamos 15 pixeles mas para la proxima label      
        precio_btc_anterior= precio_btc

        #print(fecha)

    raiz.mainloop()
    

def main():
    conexion_db()

    interfaz()

if __name__ == "__main__":
    main()