# -*- coding: utf-8 -*-
"""
Data Scraping - Submarino.com
Started on Fri May 26 00:02:46 2017

@author: Falamarcao
"""

import requests
import pandas as pd

def extrairID(codigo_fonte,inicio,fim):
  tempLst = []
  fonteID = codigo_fonte.split('"productGrid":{"items":[')[1].split('],')[0].split(',')
  for item in range(len(fonteID)):
    try:
      tempStr = fonteID[item].split(fim)[0].split(inicio)[1]
      tempLst.append(tempStr)
    except:
      tempLst.append("")
  return tempLst
  tempLst.clear()
  
def extrair(codigo_fonte,lista_IDs,inicio,fim):
  tempLst = []
  for ID in lista_IDs:
    try:
      tempStr = codigo_fonte.split("]",1)[1].split('{"id":"' + ID + '",')[1].split(inicio)[1].split(fim)[0]
      tempLst.append(tempStr)
    except:
      tempLst.append("")
  return tempLst
  tempLst.clear()

def separar_taxa_e_valor(lista_de_desconto,inicio,fim):
  tempLst = []
  for e in range(len(Descontolst)):
    try:
      tempStr = Descontolst[e].split(inicio)[1].split(fim)[0]
      tempLst.append(tempStr)
    except:
      tempLst.append("")
  return tempLst
  tempLst.clear()

def separar_atualizacao(lista_Atualizacao,Tipo):
  tempLst = []
  if Tipo == "Data": Tipo = 0
  if Tipo == "Hora": Tipo = 1
  for item in lista_Atualizacao:
    try:
      tempLst.append(item.split("T")[Tipo])
    except:
      tempLst.append("")
  return tempLst
  tempLst.clear()

def URLproduto(Lista_de_IDs):
  URL = []
  for IDstr in Lista_de_IDs:
    URL.append("https://www.submarino.com.br/produto/" + str(IDstr))
  return URL

def formatarURL_paraExcel(Nomelst,URLlst):
  tempLst = []
  for URL in URLlst:
    tempLst.append('=HYPERLINK("'+URL+'";"'+Nomelst[URLlst.index(URL)]+'")')
  return tempLst
  tempLst.clear()
  
def limparListas():
  for e in [Atualizacao,dtAtualizacao,hrAtualizacao,Nomelst, Preco_vendalst, Preco_de_listagemlst, urlImagemlst, Produtosdic, urlProdutolst, IDlst, Descontolst, taxaDlst, valorDlst]:
    e.clear()
    

KEYWORD = input("O que deseja procurar no Submarino?")
KEYWORD = KEYWORD.replace(" ","%20")

url = "https://www.submarino.com.br/busca/?conteudo="+KEYWORD+"&ordenacao=moreRelevant&origem=nanook"
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}
response = requests.get(url, headers=headers)


if response.status_code == 200:
  html = response.text
  response.close()
  html = html.split('"query":',1)[1].split('"query":')[0]
  
  IDlst = extrairID(html,'{"id":','}')
  
  Atualizacao = extrair(html, IDlst, ',"updatedAt":"', '"')
  dtAtualizacao = separar_atualizacao(Atualizacao,"Data")
  hrAtualizacao = separar_atualizacao(Atualizacao,"Hora")
  
  Nomelst = extrair(html, IDlst,'}],"name":"','","rate"')
  Preco_vendalst = extrair(html,IDlst,'","salesPrice":',',')
  Preco_de_listagemlst = extrair(html,IDlst,'","listPrice":',',')
  
  Descontolst = extrair(html,IDlst,',"discount":{','},')
  taxaDlst = separar_taxa_e_valor(Descontolst,'rate":', ',')
  valorDlst = separar_taxa_e_valor(Descontolst,'value":', ',')
  
  urlImagemlst = extrair(html,IDlst,'"big":"',',')
  urlProdutolst = URLproduto(IDlst)
  
  #EXEMPLO: =HYPERLINK("http://www.google.com.br","Google")
  #urlImagemlst = formatarURL_paraExcel(Nomelst,urlImagemlst)
  #urlProdutolst = formatarURL_paraExcel(Nomelst,urlProdutolst)

  #Inserir em dicionário e passar para Pandas.DataFrame
  Produtosdic = {"idProduto":IDlst,"Data":dtAtualizacao,"Horario":hrAtualizacao,"Nome":Nomelst,"Preço de Listagem":Preco_de_listagemlst,"Desconto(taxa)":taxaDlst,"Desconto":valorDlst,"Preço de Venda":Preco_vendalst,"Imagem":urlImagemlst,"URL":urlProdutolst}
  Produtos = pd.DataFrame(Produtosdic,index=Produtosdic["idProduto"])
  Produtos = Produtos[["Data","Horario","Nome","Preço de Listagem", "Desconto(taxa)", "Desconto","Preço de Venda","Imagem","URL"]]
  Produtos.index.name="idProduto"
  
  limparListas()
  
else:
  print("Response Code: " + str(response.status_code))
  response.close()
  pass

if Produtos.empty:
  print("Não há resultados para a pesquisa")
else:
  # Salvar para excel
  KEYWORD = KEYWORD.replace("%20","_")
  workbook = pd.ExcelWriter("Submarino_"+KEYWORD+".xlsx", engine ="xlsxwriter")
  Worksheet = Produtos.to_excel(workbook, sheet_name="Produtos", index=True)
  workbook.save()
  print("\nArquivo de excel Submarino_"+KEYWORD+".xlsx salvo!")