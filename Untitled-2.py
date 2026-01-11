def check_stock(stock, capacity):
    compteur = 0
    n = len(stock)

    for i in range(n):
        objet, quantite = stock[i]
        compteur += quantite
    
    return compteur >= capacity

check_stock([('B', 4), ('M', 5), ('0', 1)], 10)


def build_stock(L):
    stock_actuel = L[0]
    compteur = 0
    result = []

    for i in range(len(L)):
        if stock_actuel == L[i]:
            compteur+=1 
        else:
            result.append((stock_actuel , compteur))
            stock_actuel = L[i]
            compteur = 1
    
    return result 

build_stock(['A','A','A','D','D','B'])


            