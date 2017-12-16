# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 12:25:50 2017

@author: Falamarcao

Automates exporting occurrence bulletins from SSP's (São Paulo's Secretariat of Security)
"""

import re
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from os import makedirs, listdir
from os.path import exists, dirname


class Transparencia_ssp(object):
  
    def __init__(self):
      
        if not exists(str(dirname(__file__))+ r'/Data/Transparencia_ssp'):
          makedirs(str(dirname(__file__))+ '/Data/Transparencia_ssp')
        
        self.url = "http://www.ssp.sp.gov.br/transparenciassp/Consulta.aspx"
    
        self.webdriver = webdriver
          
        #Download Folder
        chrome_options = self.webdriver.ChromeOptions()
        prefs = {"download.default_directory": str(dirname(__file__))+"/Data/Transparencia_ssp",
                 "download.prompt_for_download": False,
                 "download.directory_upgrade": True}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--incognito")
        
        #WEB BROWSER - CHROME
        executable_path = r'C:\........................\chromedriver.exe' #set chromedriver path
        self.browser =  self.webdriver.Chrome(executable_path, chrome_options=chrome_options)
        self.browser.get(self.url)
        self.browser.set_script_timeout(18000)
    
  
    def ExportBO(self):
        
        bs = BeautifulSoup(self.browser.page_source, "html.parser")
        lstNature = [link.get('id') for link in bs.findAll('a', {"class": re.compile("dynWidth block")})][1:]
        
        #MISSING - TO CONTINUE
        #lstNature = ['cphBody_btnFurtoCelular',
        #             'cphBody_btnRouboCelular']
        
        for nature in lstNature:
          
            #SELECT A NATURE
            self.browser.find_element_by_xpath('//*[@id="'+nature+'"]').send_keys("\n")        
            
            #COLLECT YEARS AND MONTHS
            bs = BeautifulSoup(self.browser.page_source, "html.parser")
            
            if nature != 'cphBody_btnIML':
                lstYears = [link.get('id') for link in bs.findAll('a', {"id": re.compile("cphBody_lkAno")})]
                lstMonths = [link.get('id') for link in bs.findAll('a', {"id": re.compile("cphBody_lkMes")})]
            
            #SPECIAL CASE
            else:
                lstYears = [link.get('id') for link in bs.findAll('a', {"id": re.compile("cphBody_lkIML")})]
                lstMonths = [link.get('id') for link in bs.findAll('a', {"id": re.compile("cphBody_LinkButton")})]
            
            
            if nature != 'cphBody_btnMorteSuspeita':
                
                for year in lstYears:
                    #SELECT AN YEAR
                    self.browser.find_element_by_xpath('//*[@id="'+year+'"]').send_keys("\n")
                    sleep(3)
                    
                    for month in lstMonths:
                      
                        #SELECTING A MONTH
                        self.browser.find_element_by_xpath('//*[@id="'+month+'"]').send_keys("\n")
                        sleep(3)
                        
                        #
                        number_of_files_before_download = len(listdir(str(dirname(__file__))+ r'/Data/Transparencia_ssp'))
                        
                        #DOWNLOAD
                        print('Exporting from website...')
                        if nature != 'cphBody_btnIML':
                          
                            self.browser.find_element_by_xpath('//*[@id="cphBody_ExportarBOLink"]').send_keys(self.webdriver.common.keys.Keys.SPACE)
                                                  
                        else: #special case IML
                            self.browser.find_element_by_xpath('//*[@id="cphBody_ExportarIMLButton"]').send_keys(self.webdriver.common.keys.Keys.SPACE)
                        
                        # Waiting for the export has completed
                        if nature in ['cphBody_btnFurtoCelular', 'cphBody_btnRouboCelular']: # these topics are too slow...
                            while True:
                                self.browser.implicitly_wait(3)
                                sleep(3)
                                if number_of_files_before_download != len(listdir(str(dirname(__file__))+ r'/Data/Transparencia_ssp')):  break
                        else:
                            sleep(3)
      
            #SPECIAL CASE 'Morte Suspeita' because has subtopics
            else:
                lstMorteSuspeita = [link.get('id') for link in bs.findAll('a', {"id": re.compile("cphBody_btnMorteSuspeita")})][1:]
                
                for mortesuspeita in lstMorteSuspeita:
                  
                    #SELECT A 'Morte Suspeita'
                    self.browser.find_element_by_xpath('//*[@id="'+mortesuspeita+'"]').send_keys("\n")
                    
                    for year in lstYears:
                        #SELECT AN YEAR
                        self.browser.find_element_by_xpath('//*[@id="'+year+'"]').send_keys("\n")
                        
                        for month in lstMonths:
                          
                            #SELECT A MONTH
                            sleep(3)
                            self.browser.find_element_by_xpath('//*[@id="'+month+'"]').send_keys("\n")
                            
                            
                            #
                            number_of_files_before_download = len(listdir(str(dirname(__file__))+ r'/Data/Transparencia_ssp'))
                            
                            #DOWNLOAD FILE
                            print('Exporting from website...', nature, month, year)
                            sleep(3)
                            self.browser.find_element_by_xpath('//*[@id="cphBody_ExportarBOLink"]').send_keys(self.webdriver.common.keys.Keys.SPACE)  
                            sleep(3)

                  
    def close(self):
        self.browser.implicitly_wait(10)
        self.browser.quit()
        return "WebScraping from URL: '"+self.url+"' finished!\n \
                Please check your files in the folder."


if __name__ == '__main__':
  
    #Scraping = Transparencia_ssp()
    #Scraping.ExportBO()
    #Scraping.close()
    
    from boxoftools.Files_Handling import DataFrame_utils
    
    def transparenciassp():
          transparenciassp = DataFrame_utils(root=r'C:\Users\Falamarcao\Documents\Python Scripts\Desafio_PrefeituraSP')
          transparenciassp.read_csv_args = {"sep": '\t', "quoting": 3, "encoding": 'unicode_internal'}
          transparenciassp.concatenate(folders_path=r'Data\(parte1)Transparencia_ssp', parallel_reading=True, cores=16)
          transparenciassp.output_filter(filter_column='CIDADE', filter_value='S.PAULO')
          transparenciassp.save_to_csv()
      
    def SAC_SP156():
          SAC_SP156 = DataFrame_utils(root=r'C:\Users\Falamarcao\Documents\Python Scripts\Desafio_PrefeituraSP')
          SAC_SP156.read_csv_args = {"sep": ';', "quoting": 0, "encoding": 'ANSI'}
          SAC_SP156.concatenate(folders_path=r'Data\SAC_SP156', parallel_reading=True, cores=16)
          SAC_SP156.save_to_csv()
          del SAC_SP156
      
    transparenciassp()
    SAC_SP156()