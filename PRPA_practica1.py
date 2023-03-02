"""
Created on Mon Feb 27 16:02:07 2023

@author: Alvaro Ezquerro

PRPA 2023: Practica 1
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array, Manager
from random import shuffle, randint
import time

NPROD=10  #Numero de Productores
K=10   #Tamaño cada 'almacen' de productor
N=20  #Cantidad de numeros que produce cada productor
    
def add_dato(almacen, indice, dato, smutex):
    smutex.acquire()
    almacen[indice.value] = dato
    indice.value = indice.value + 1
    smutex.release()

def get_dato(almacen, indice, smutex):
    smutex.acquire()
    dato = almacen[0]
    indice.value = indice.value - 1
    for i in range(indice.value):
        almacen[i] = almacen[i + 1]
    almacen[indice.value] = -2
    smutex.release()
    return dato

def productor(almacen, indice, sproducir: BoundedSemaphore, sconsumir:Semaphore, 
              smutex: Lock):
    dato=0
    for v in range(N):
        print (f"Productor {current_process().name} produciendo")
        dato+=randint(0,20)
        sproducir.acquire()                  
        add_dato(almacen, indice, dato, smutex)
        sconsumir.release()
        print (f"Productor {current_process().name} almacenado {dato}")
    sproducir.acquire() 
    add_dato(almacen, indice, -1, smutex)
    print (f"Productor {current_process().name} ha finalizado")

def mi_minimo(lista):
    """
    Dada la lista de elementos de productores, devuelve el indice del
    productor con el elemento minimo
    """
    (indice, m)=lista[0]
    for (ind, elem) in lista[1:]:
        if elem<m:
            m=elem
            indice=ind
    lista.remove((indice, m))
    return indice

def estado_actual(almacenes, lista):
    """
    Funcion que imprime el estado actual de la lista y los almacenes
    """
    print("\n\n\nLa lista actual es: "+str(lista), flush=True)
    print('\nLongitud actual de la lista: '+str(len(lista)), flush=True)
    print('\nLos almacenes actuales son:', flush=True)
    for almacen in almacenes:
        result=''
        for k in range(len(almacen)):
            result=result+str(almacen[k])
            result+=' '
        print(result, flush=True)
    print('\n\n\n')
        
def consumidor(almacenes, indices, sprod_lst, scons_lst, smutex_lst, lista):
    """
    Se puede añadir en cualquier lugar la funcion estado_actual y ver como
    van cambiando los almacenes y la lista final
    """
    
    terminados=set()  #Indices de productores que han acabado de producir
    
    "Esperamos a que todos hayan producido"
    for i in range(NPROD):
        scons_lst[i].acquire()
        
    "Leemos todos los almacenes y tomamos el indice del minimo"   
    aux=[] 	#Lista auxiliar para calcular el minimo en cada vuelta
    for i in range(NPROD): 
        valor=almacenes[i][0]
        if valor==-1:
            terminados.add(i)
        else:
            aux.append((i, valor))
    j=mi_minimo(aux)
      
    while len(terminados)<len(almacenes):
        #estado_actual(almacenes, lista)
        
        print (f"Consumidor desalmacenando almacen {j}")
        scons_lst[j].acquire()
        dato=get_dato(almacenes[j], indices[j], smutex_lst[j])
        lista.append((j, dato))
        sprod_lst[j].release()
        print (f"Consumidor a consumido {dato} del almacen {j}")
            
        valor=almacenes[j][0]
        if valor==-1:
            terminados.add(j)
        else:
            aux.append((j, valor))
            
        if aux!=[]:
        	j=mi_minimo(aux)
        
        
            
def main():
    """
    Creamos el consumidor, K almacenes vacios, K productores,
    K indices, K semaforos, K locks y K boundedsemaphores.
    """
    manager=Manager()
    lista=manager.list()    #Lista solucion de pares (productor, valor)
    prod_lst=[]
    alm_lst=[]
    ind_lst=[]
    scons_lst=[]    #Semaforos que indican si se puede consumir
    sprod_lst=[]    #Semaforos que indican si se puede producir
    smutex_lst=[]      #Locks para la seccion critica
    for i in range(NPROD):
        sconsumir=Semaphore()
        scons_lst.append(sconsumir)
        
        sproducir=BoundedSemaphore(K)
        sprod_lst.append(sproducir)
       
        smutex=Lock()
        smutex_lst.append(smutex)
        
        indice=Value('i', 0)
        ind_lst.append(indice)
        
        almacen = Array('i',K)
        for j in range(K):
            almacen[j]=-2
        alm_lst.append(almacen)
        
        nombre='prod_'+str(i)
        prod=Process(target=productor, name=nombre,
                            args=(almacen, indice, sproducir, 
                                  sconsumir, smutex))
        prod_lst.append(prod)   
        
    cons=Process(target=consumidor, name='consumidor', 
                      args=(alm_lst, ind_lst, sprod_lst, 
                            scons_lst, smutex_lst, lista))
        
     
    "Iniciamos todos los procesos"
    cons.start()
    for proceso in prod_lst:
        proceso.start()
    
    
    "Finalizacion de los procesos"
    cons.join()
    for proceso in prod_lst:
        proceso.join()
        
    "Imprimimos los diferentes almacenes y la lista del consumidor"
    
    print("\n\n\nLa lista final es: "+str(lista), flush=True)
    print('\nLongitud final de la lista: '+str(len(lista)), flush=True)
    print('\nLos almacenes finales son:', flush=True)
    for almacen in alm_lst:
        result=''
        for k in range(len(almacen)):
            result=result+str(almacen[k])
            result+=' '
        print(result, flush=True)
    print('\n\n\n')

if __name__=='__main__':
    main()
