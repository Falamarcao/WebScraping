# -*- coding: utf-8 -*-
"""
Data Scraping - Submarino.com

Created on Wed May 31 04:26:03 2017
Version: 3
@author: Falamarcao
"""
import requests
import json
from tqdm import trange
from numpy import nan
import pandas as pd

def JSON(source_code):
  source_code = source_code.split("<script>window.INITIAL_STATE = ")[1].split("</script>")[0][0:-1]
  return json.loads(source_code)

def extrairID(jsonlst):
  tempLst = []
  for item in range(len(jsonlst)):
      for ID in range(len(jsonlst[item]["productGrid"]["items"])):
        tempStr = jsonlst[item]["productGrid"]["items"][ID]["id"]
        tempLst.append(tempStr)
        #ver se há dados completos para cada ID, se nao houver ele retira da lista
        try:
          jsonlst[item]["products"]["refs"][str(tempStr)]["offers"]
        except:
          tempLst.remove(tempStr)
          tempLst.append("")          
  return tempLst
  del tempLst, tempStr

def extrairOferta_IDProduto(jsonlst,Lista_ID,Campo_procurado1):
  tempLst = []
  i = 0
  f = 24
  for item in range(len(jsonlst)):
    for ID in Lista_ID[i:f]:
      #verifica se o ID está vazio - Vamos reservar um espaço para não desordenar a lista.
      if ID != "":
        temp = jsonlst[item]["products"]["refs"][str(ID)]["offers"]
        for e in range(len(temp)):  
            tempLst.append(ID)
      elif ID == "":
        tempLst.append("")
    i += 24
    f += 24
  return tempLst
  del tempLst, temp, i, f, e

def extrair(jsonlst,Lista_ID,Campo_procurado):
  tempLst = []
  i = 0
  f = 24
  for item in range(len(jsonlst)):
    for ID in Lista_ID[i:f]:
      #verifica se o ID está vazio - Vamos reservar um espaço para não desordenar a lista.
      if ID != "":        
        tempStr = jsonlst[item]["products"]["refs"][str(ID)][Campo_procurado]
        tempLst.append(tempStr)
      elif ID == "":
        tempLst.append("")
    i += 24
    f += 24
  return tempLst
  del tempLst

def extrairOferta(jsonlst,Lista_ID,Campo_procurado1,Campo_procurado2=None,Campo_procurado3=None,Campo_procurado4=None,dtAtualizacao=None):
  tempLst = []
  i = 0
  f = 24
  for item in range(len(jsonlst)):
    for ID in Lista_ID[i:f]:
      #verifica se o ID está vazio - Vamos reservar um espaço para não desordenar a lista.
      if ID != "":        
        for e in range(len(jsonlst[item]["products"]["refs"][str(ID)]["offers"])):
          try:  
            temp = jsonlst[item]["products"]["refs"][str(ID)]["offers"]
            if dtAtualizacao == 1:
              temp = temp[e][Campo_procurado1]
              temp = temp.replace("T"," ")
            elif (Campo_procurado2 == None and Campo_procurado3 == None and Campo_procurado4 == None):
              temp = temp[e][Campo_procurado1]
            elif (Campo_procurado2 != None and Campo_procurado3 == None and Campo_procurado4 == None):
              temp = temp[e][Campo_procurado1][Campo_procurado2]
            elif (Campo_procurado2 != None and Campo_procurado3 != None and Campo_procurado4 == None):
              temp = temp[e][Campo_procurado1][Campo_procurado2][Campo_procurado3]
            elif (Campo_procurado2 != None and Campo_procurado3 != None and Campo_procurado4 != None):
              temp = temp[e][Campo_procurado1][Campo_procurado2][Campo_procurado3][Campo_procurado4]
            tempLst.append(temp)
          except:
            tempLst.append("")
      elif ID == "":
         tempLst.append("")
    i += 24
    f += 24
  return tempLst
  del tempLst, temp, i, f

def extrairFoto(FotosDic):
  tempLst = []
  for e in range(len(FotosDic)):
    for tamanho in ["extraLarge","large","big","medium"]:
      try:
        #verifica se a posição está vazia - Vamos reservar um espaço para não desordenar a lista.
        if FotosDic[e] == "":
          tempLst.append("")
          break
        tempLst.append(FotosDic[e][0][tamanho])
        break
      except:
        if tamanho == "medium":
          #se chegou aqui é pq o site não tem foto do produto. Vamos reservar um espaço para não desordenar a lista.
          tempLst.append("")
  return tempLst
  del tempLst
  
def URLproduto(Lista_de_IDs):
  URL = []
  for ID in Lista_de_IDs:
    #verifica se a posição está vazia - o espaço só pode ser retirado no final para não atrapalhar os For loops
    if ID != "":
      URL.append("https://www.submarino.com.br/produto/" + str(ID))
    elif ID == "":
      URL.append("")
  return URL

def limparListas():
  for e in [ID_Produtolst,Nomelst,urlImagemlst,urlProdutolst,ID_Vendedorlst,NomeVendedorlst,PrecoListagemlst,PrecoVendalst,txDesclst,vlDesclst,dtAtualizacaolst,Condicaolst,Estoquelst]:
    e.clear()
 
# Captura palavra-chave para realizar pesquisa
KEYWORD = input("O que deseja procurar no Submarino?")
KEYWORD = KEYWORD.replace(" ","%20")

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}

# Abre sessão
session = requests.session()

Lista_Json = []
offset = 0

# Captura total de resultados
url = "https://www.submarino.com.br/busca/?conteudo="+KEYWORD+"&limite=24&offset="+str(offset)+"&ordenacao=moreRelevant"
response = session.get(url, headers=headers)
Lista_Json.append(JSON(response.text))
Resultados_Encontrados = Lista_Json[0]["pagination"]["total"]

# RANGE DE PESQUISA
if Resultados_Encontrados == 0:
  print("Não há resultados para a pesquisa")
elif Resultados_Encontrados > 0:
  
  print("Foram encontrados "+str(Resultados_Encontrados)+" produtos com a palavra-chave "+KEYWORD.replace("%20"," ")+".")
  Range_Pesquisa = float(input("Qual % deseja retornar na sua pesquisa? (Ex: 5  5.5  50)"))
  Range_Pesquisa = int((Resultados_Encontrados * Range_Pesquisa)/100)
  
  # Transforma Range em multiplo de 24 para saber quantos produtos serão capturados
  # obs:. o grid do submarino exibe os produtos de 24 em 24
  while Range_Pesquisa % 24 != 0:
    if Range_Pesquisa <= 24:
      Range_Pesquisa = 24
      break
    elif Range_Pesquisa > 24 and Range_Pesquisa % 24 != 0:  
      Range_Pesquisa += 1
  
# Confirmação da pesquisa
  while True:
    continuar = input("Serão retornados aprox. "+str(Range_Pesquisa)+" resultados. Deseja Continuar? (s/n)") 
    if continuar == "n":
      print("\nPesquisa encerrada pelo usuário.")
      break
    elif continuar == "s":
      n = int(Range_Pesquisa/24)
      
#     Coleta os arquivos Json  
      while n > 1:
        for barra_Progreso in trange(n-1, desc="Extraindo dados do site submarino.com"): #barra de progesso tqdm
          url = "https://www.submarino.com.br/busca/?conteudo="+KEYWORD+"&limite=24&offset="+str(offset)+"&ordenacao=moreRelevant"
          response = session.get(url, headers=headers)
          if response.status_code == 200:
            Lista_Json.append(JSON(response.text))
          else:
            Lista_Json.append("Offset: "+str(offset)+". Response Code: " +str(response.status_code))
          offset += 24
          n -= 1
      
      del n, offset, continuar, headers
      session.close()
      response.close()
      
#     Processa os dados preenchendo campos para listas -> dicionario -> pandas.DataFrame
      if len(Lista_Json) > 0:
        for barra_Progresso in trange(int(Range_Pesquisa/24), desc="Processamento de informações"):
          
          ID_Produtolst = extrairID(Lista_Json)
          Nomelst = extrair(Lista_Json,ID_Produtolst,"name")
          urlImagemlst = extrairFoto(extrair(Lista_Json,ID_Produtolst,"images"))
          urlProdutolst = URLproduto(ID_Produtolst)
          
          ID_Produtolst_Ofertas = extrairOferta_IDProduto(Lista_Json,ID_Produtolst,"id")
          ID_Vendedorlst = extrairOferta(Lista_Json,ID_Produtolst,"_embedded","seller","id",None)
          ID_Ofertalst = extrairOferta(Lista_Json,ID_Produtolst,"id",None,None,None)
          NomeVendedorlst = extrairOferta(Lista_Json,ID_Produtolst,"_embedded","seller","name",None)
          PrecoVendalst = extrairOferta(Lista_Json,ID_Produtolst,"salesPrice",None,None,None)
          PrecoListagemlst = extrairOferta(Lista_Json,ID_Produtolst,"listPrice",None,None,None)
          Condicaolst = extrairOferta(Lista_Json,ID_Produtolst,"condition",None,None,None)
          txDesclst = extrairOferta(Lista_Json,ID_Produtolst,"discount","rate",None,None)
          vlDesclst = extrairOferta(Lista_Json,ID_Produtolst,"discount","value",None,None)
          Estoquelst = extrairOferta(Lista_Json,ID_Produtolst,"availability","_embedded","stock","quantity")
          dtAtualizacaolst = extrairOferta(Lista_Json,ID_Produtolst,"updatedAt",None,None,None,dtAtualizacao=1)
          
          
          Produtosdic = {"idProduto":ID_Produtolst,"Nome_produto":Nomelst,"Imagem":urlImagemlst,"URL":urlProdutolst}
          
          Ofertasdic = {"idProduto":ID_Produtolst_Ofertas,"idVendedor":ID_Vendedorlst,"ID_Oferta":ID_Ofertalst,"Nome_vendedor":NomeVendedorlst,"Preço_lista":PrecoListagemlst,"Preço_venda":PrecoVendalst,"Condicao":Condicaolst,"Taxa_Desc":txDesclst,"Valor_Desc":vlDesclst,"Estoque":Estoquelst,"Atualização":dtAtualizacaolst}
          
#         Pandas.DataFrame
          Produtos = pd.DataFrame(Produtosdic)
          Produtos = Produtos[["idProduto","Nome_produto","Imagem","URL"]]
          
          Ofertas = pd.DataFrame(Ofertasdic)
          Ofertas = Ofertas[["idProduto","idVendedor","ID_Oferta","Nome_vendedor","Preço_lista","Preço_venda","Taxa_Desc","Valor_Desc","Condicao","Estoque","Atualização"]]
          
          #JOINED
          Inner_join = pd.merge(Produtos,Ofertas, on="idProduto")
          Inner_join = Inner_join[["idProduto","Atualização","Nome_produto","Nome_vendedor","ID_Oferta","Preço_lista","Taxa_Desc","Valor_Desc","Preço_venda","Condicao","Estoque","Imagem","URL"]]
          
          #Duplicatas
          if Inner_join.duplicated().sum() > 0:
            Inner_join = Inner_join.drop_duplicates(subset = "ID_Oferta", keep="last")
          
          #Apagar linhas em branco (produtos fora de estoque)
          Inner_join = Inner_join.replace("",nan)
          Inner_join = Inner_join.dropna(how="all")
          Inner_join = Inner_join.replace(nan,"")
          
          #Limpa Listas usadas (estético para o Spyder)
          limparListas()
          
#       Salva para excel
        if input("Deseja Salvar para excel(s/n)?") == "s":          
          KEYWORD = KEYWORD.replace("%20","_")
          workbook = pd.ExcelWriter("Submarino_"+KEYWORD+".xlsx", engine ="xlsxwriter")
          Worksheet = Inner_join.to_excel(workbook, sheet_name="Geral", index=False)
          workbook.save()
          print("\nArquivo de excel Submarino_"+KEYWORD+".xlsx salvo!")
          
      break # EOF