# -*- coding: utf-8 -*-
"""
Data Scraping - Submarino.com
Created on Fri May 26 00:02:46 2017

@author: Falamarcao
"""

import requests
import pandas as pd

def extrair(codigo_fonte,inicio,fim):
  tempLst = []
  lista_produtos = html.split("<footer")[0].split(inicio)[1:]
  for produto in range(len(lista_produtos)):
    tempStr = lista_produtos[produto].split(fim)[0]
    tempLst.append(tempStr)
  return tempLst
  tempLst.clear()
  
def extrairURLproduto(codigo_fonte,inicio,fim):
  tempLst = []
  lista_produtos = html.split("<footer")[0].split(inicio)[1:]
  for produto in range(len(lista_produtos)):
    tempStr = lista_produtos[produto].split(fim)[0]
    tempLst.append("https://www.submarino.com.br" + tempStr)
  return tempLst
  tempLst.clear()

def formatarURL_paraExcel(Nomelst,URLlst):
  tempLst = []
  for URL in URLlst:
    tempLst.append('=HYPERLINK("'+URL+'";"'+Nomelst[URLlst.index(URL)]+'")')
  return tempLst
  tempLst.clear()
  
def limparListas():
  for e in [Nome, Preco, urlImagem, Produtosdic, urlProduto]:
    e.clear()

KEYWORD = input("O que deseja procurar no Submarino?")
KEYWORD = KEYWORD.replace(" ","%20")

url = "https://www.submarino.com.br/busca/?conteudo="+KEYWORD+"&ordenacao=moreRelevant&origem=nanook"
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}
response = requests.get(url, headers=headers)

if response.status_code == 200:
  html = response.text
  response.close()
  ID = extrair(html, '","url":"/produto/','?')
  Nome = extrair(html,'{"@context":"https://www.schema.org","@type":"product","name":"','","image":')
  Preco = extrair(html,'"priceCurrency":"BRL","price":',',"itemCondition"')
  urlImagem = extrair(html,'"><source srcset="',',')
  urlProduto = extrairURLproduto(html,',"url":"','","')
  #EXEMPLO: =HYPERLINK("http://www.google.com.br","Google")
  #urlImagem = formatarURL_paraExcel(Nome,urlImagem)
  #urlProduto = formatarURL_paraExcel(Nome,urlProduto)
  Produtosdic = {"idProduto":ID, "Nome":Nome, "Preço":Preco, "Imagem":urlImagem, "URL":urlProduto}
  Produtos = pd.DataFrame(Produtosdic)
  Produtos = Produtos[["idProduto","Nome","Preço","Imagem","URL"]]
  limparListas()
else:
  print("Response Code: " + str(response.status_code))
  response.close()

if Produtos.empty:
  print("Não há resultados para a pesquisa")
else:
  # Salvar para excel
  KEYWORD = KEYWORD.replace("%20","_")
  workbook = pd.ExcelWriter("Submarino_"+KEYWORD+".xlsx", engine ="xlsxwriter")
  Worksheet = Produtos.to_excel(workbook, sheet_name="Produtos", index=False)
  workbook.save()
  print("Arquivo de excel Submarino_"+KEYWORD+".xlsx salvo!")  