# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 16:27:07 2017

@author: Falamarcao

DataScraping:
Governo do Estado de São Paulo / SSP - TRANSPARÊNCIA
"""

import requests
from lxml.html import document_fromstring

class Transparencia_ssp(object):
    
    def __init__(self):
        self.sess = requests.Session()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/62.0.3202.94 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}
        
        self.url = "http://www.ssp.sp.gov.br/transparenciassp/Consulta.aspx/AbrirBoletim"
        self.viewstate = self.sess.get(self.url, headers=self.headers).text.split('id="__VIEWSTATE" value="')[1].split('" />')[0]
        self.eventvalidation = self.sess.get(self.url, headers=self.headers).text.split('id="__EVENTVALIDATION" value="')[1].split('" />')[0]

    def get_years_months_list(self, html):
      
      html = document_fromstring(html)
      elementYears  = html.xpath('//*[@id="cphBody_divDados"]/div[1]/ul/li')
      elementMonths  = html.xpath('//*[@id="cphBody_divDados"]/div[2]/ul/li')
      
      return [[subelement for element in elementYears for subelement in element.xpath('a//text()')], 
               [subelement for element in elementMonths for subelement in element.xpath('a//text()')]]
      
    def requestBO(self, **kwargs):
      
      #insert the state 0
      viewstate = self.viewstate
      eventvalidation = self.eventvalidation
      
      for key, value in kwargs.items():
        formData = [
            ("__VIEWSTATE", viewstate),
            ("__EVENTVALIDATION", eventvalidation),
        ]
        
        #add paramters to send requests
        formData.append((key,value))
        
        #collect the data
        content = self.sess.post(self.url, data=formData, headers=self.headers)
        
        # if have a next kwargs
        if list(kwargs.keys()).index(key) < len(kwargs):
          #update viewstate and eventvalidation
          viewstate = content.text.split('id="__VIEWSTATE" value="')[1].split('" />')[0]
          eventvalidation = content.text.split('id="__EVENTVALIDATION" value="')[1].split('" />')[0]
        
        formData.remove((key,value))
        
      return content.text
    
    def initial_state(self):
      
      Scrapping = Transparencia_ssp()
    
      _kwargs = {"__EVENTTARGET": "ctl00$cphBody$btnHomicicio",
               "ctl00$cphBody$filtroDepartamento": "500000"}
      strInitial_state = Scrapping.requestBO(**_kwargs)
    
      #_kwargs = {"__EVENTTARGET": "ctl00$cphBody$lkMes1"}
      #strInitial_state = Scrapping.requestBO(**_kwargs)
      
      return strInitial_state
  
    
    def end(self):
        self.sess.close()


if __name__ == '__main__':
  
  Scrapping = Transparencia_ssp()
  
  initial_state = Scrapping.initial_state()
  
  years = Scrapping.get_years_months_list(initial_state)
  
  print(years)
  
  #with open('teste.html','w') as file:
  #    file.write(years)
  #    file.close
  
  Scrapping.end()
        