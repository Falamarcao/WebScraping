# -*- coding: utf-8 -*-
"""
---------------------------------------
Portal do MEI - Receita.Fazenda.gov.br
---------------------------------------
TOTAL GERAL DE MICROEMPREENDEDORES INDIVIDUAIS

  - Acumulado UF/Município por código CNAE, descrição CNAE e Sexo
  - Total de Empresas Optantes no SIMEI, da Unidade Federativa SP, 
      Município SAO PAULO, por Código CNAE, descrição CNAE e Sexo.

Created on Sun Jun  4
"""
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from tqdm import tqdm, trange
from unidecode import unidecode
from time import sleep
import datetime
import lxml.html
import pandas as pd

class ErrorHandling:
  
  _Coletar_ERROS = []
  _tentativa = 0
  _contaerros = 0
  _Erros = pd.read_excel("Município.xlsx",sheetname="Erros")
  
class Dados():
  #lista de cidades/UF
  localidades = pd.read_excel("Município.xlsx",sheetname="Municípios")

class MEI():
  
  #bw = wd.Chrome(executable_path = r"C:\.......\chromebw.exe") #bw de testes
  
  user_agent = "Mozilla/5.0 (Windows NT 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
  webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = user_agent

  bw = webdriver.PhantomJS(service_args=["--webdriver-loglevel=SEVERE"]) #browser sem interface gráfica
  
  #navega até o site e clica no link
  URL="http://www22.receita.fazenda.gov.br/inscricaomei/private/pages/relatorios/opcoesRelatorio.jsf#"
  bw.get(URL)
  bw.find_element_by_xpath('//*[@id="form"]/div/dl[3]/dt[7]/a').click()
  

  def Consulta_para_DataFrame(ID_LOCALIDADE,UF,Cidade):
    
    while True:
      
      #Preenche, UF, Cidade,clica em Consultar no site e retorna o codigo-fonte
      cboUF = Select(MEI.bw.find_element_by_xpath('//*[@id="form:uf"]'))
      cboUF.select_by_value(UF)
       
      #Modifica o valor de cidade para ser compativel com o Site
      tempCidade = Cidade.replace("'"," ").replace("-"," ").replace("D ","D")
      tempCidade = unidecode(tempCidade).upper()
      
      #Substituição temporária de nomes
      if ID_LOCALIDADE in ErrorHandling._Erros["idCidade"]:
        tempCidade = ErrorHandling._Erros["Cidade_Adpt"].loc[ErrorHandling._Erros['idCidade'] == ID_LOCALIDADE]
      
      cboCidade = Select(MEI.bw.find_element_by_xpath('//*[@id="form:municipioUF"]'))
      
      #O site tem um tempo de carregamento lento e as vezes ocorre erros
     
      try:
        ErrorHandling._tentativa += 1
        tqdm.write("Tentativa n. "+str(ErrorHandling._tentativa))
        sleep(0.8*ErrorHandling._tentativa)
        cboCidade.select_by_visible_text(tempCidade)
        ErrorHandling._tentativa = 0
        break
      except:
        pass
      
      if ErrorHandling._tentativa == 3:
          tqdm.write("REFRESH! TENTANDO NOVAMENTE..")
          MEI.bw.refresh()
          sleep(2)
      elif ErrorHandling._tentativa == 8: break
    
    if ErrorHandling._tentativa == 8:
      ErrorHandling._contaerros += 1
      tqdm.write("N. DE ERROS: "+str(ErrorHandling._contaerros))
      ErrorHandling._Coletar_ERROS.append({"ID_LOCALIDADE":ID_LOCALIDADE,"Cidade":tempCidade,"Uf":UF})
      ErrorHandling._tentativa = 0
      return
    
    MEI.bw.find_element_by_xpath('//*[@id="form:botaoConsultar"]').click()
    codigo_fonte = MEI.bw.page_source
    
    #usando a biblioteca lxml
    pagina = lxml.html.fromstring(codigo_fonte)
    #//*[@id="form:j_id31"]/*[@id="form:j_id31:tb"] -> TABELA  /tr -> LINHAS DA TABELA
    lstLinhas = pagina.xpath('//*[@id="form:j_id31"]/*[@id="form:j_id31:tb"]/tr')
    
    #Dicionário para armazenar os dados
    dicTEMP ={"ID_LOCALIDADE":[],"UF":[],"CIDADE":[],"COD_CNAE":[],"DESCRICAO_CNAE":[],"TOTAL_MEI":[],"HOMENS_MEI":[],"MULHERES_MEI":[]}
    rotulos = ["COD_CNAE","DESCRICAO_CNAE","TOTAL_MEI","HOMENS_MEI","MULHERES_MEI"]
    
    #for linha in range(len(lstLinhas)):
    for linha in trange(len(lstLinhas), desc="Extraindo tabela "+Cidade+"/"+UF): #barra de progesso tqdm
      #adiciona a coluna da UF e Cidade
      dicTEMP["ID_LOCALIDADE"].append(ID_LOCALIDADE)
      dicTEMP["UF"].append(UF)
      dicTEMP["CIDADE"].append(Cidade)
      for coluna, rotulo  in zip(range(1,6),rotulos):
        strTemp = lstLinhas[linha].xpath('td['+str(coluna)+']//text()')[0]
        dicTEMP[str(rotulo)].append(strTemp)
     
    return pd.DataFrame(dicTEMP) 
  
  def Executar(localidades):
    lstDataFrames = []
    for idlocalidade, uf, cidade in zip(localidades["idCidade"],localidades["Uf"],localidades["Cidade"]):
      tqdm.write("-----------------"+cidade+"/"+uf+"-----------------")
      tempDF = MEI.Consulta_para_DataFrame(idlocalidade, uf, cidade)
      if type(tempDF) == pd.core.frame.DataFrame:
        lstDataFrames.append(tempDF)
        tqdm.write("Concluído\n")
        tempDF = None
      else:
        continue
    MEI.bw.quit()
    return lstDataFrames
  
  def Compilar_resultados(lstDataFrames):
    #Data Frame com os resultados
    if len(lstDataFrames) > 0: #Caso tenha mais de um une/concatena os Data Frames
      Resultado = pd.concat(lstDataFrames)
      Resultado = Resultado[["ID_LOCALIDADE","UF","CIDADE","COD_CNAE","DESCRICAO_CNAE","TOTAL_MEI","HOMENS_MEI","MULHERES_MEI"]]
      Resultado.to_csv("Portal_MEI ("+str(datetime.datetime.now()).replace(":","_")[:-7]+").csv",index=False)
 
    if len(ErrorHandling._Coletar_ERROS) > 0:
      DEBUG = pd.DataFrame(ErrorHandling._Coletar_ERROS)
      DEBUG.to_csv("DEBUG_Portal_MEI ("+str(datetime.datetime.now()).replace(":","_")[:-7]+").csv",index=False)

if __name__ == "__main__":
  try:
    #extrai lista de DataFrames das localidades
    lstDataFrames = MEI.Executar(Dados.localidades)
  except:
    pass
  
  #compila Resultados e lista de erros para *.csv
  MEI.Compilar_resultados(lstDataFrames)
