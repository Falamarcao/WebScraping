# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 16:32:39 2017

@author: Falamarcao

Python class to read old xls files and concatenate Pandas.DataFrames saving to a *.csv 
"""

from os import chdir, listdir, makedirs
from os.path import exists, basename
from datetime import datetime
from tqdm import trange
from time import time
import pandas as pd




class DataFrame_utils(object):
  
    def __init__(self, root):
      self.start_time = time()
      if root[-1] not in ['/', '\x07', '\\']: root += '\\'
      self.root = root.replace('/','\\')      
      self.reading_errors = []
      self.concatenation_directory = ''
      self.filter_column = None
      self.filter_value = None
      self.OutputDataFrame = None
      self.read_csv_args = []
      
    
    def cd(self, src):
        chdir(src)
        return print("Working on: " + src)
      
      
    def read_csv(self, file):
        try:
            return pd.read_csv(file, sep=self.read_csv_args["sep"], quoting=self.read_csv_args["quoting"], 
                               encoding=self.read_csv_args["encoding"], engine='python')
        except Exception as e:
            self.reading_errors.append({"Error": e, "File": file})
            
            
    def errors_folder(self, src):
        if len(self.reading_errors) > 0:
            from shutil import copy2
            for element in self.reading_errors:
                copy2(self.concatenation_directory + '\\' +  element["File"], self.root + r'\Errors')
            print("Please, check Errors folder")


    def concatenate(self, folders_path, lstfiles=None, parallel_reading=False, cores=1):
        
        self.concatenation_directory = self.root + folders_path.replace('/','\\')   
        
        self.cd(self.concatenation_directory)
        
        if lstfiles == None: lstfiles = listdir()
        
        if type(lstfiles) is list and len(lstfiles) > 1:
            
            if parallel_reading:
                print('Parallel processing has started...')
                from multiprocessing import Pool
                pool = Pool(cores)
                self.OutputDataFrame = pd.concat(pool.map(self.read_csv, [file for file in lstfiles]))
                pool.close()
                pool.join()
                print('Parallel processing has finished...')
                #self.OutputDataFrame = OutputDataFramePool
            else:
              self.OutputDataFrame = pd.concat([self.read_csv(file) for _, file in zip(trange(len(lstfiles)), lstfiles)])
            
            #read_csv() erros
            if len(self.reading_errors) == 0:
                print("Concatenate process completed with Sucess!")
            else:
                print("Concatenate process completed with errors")
                self.errors_folder(self.concatenation_directory)     
        
        #if is only 1 file there is not why to concatenate
        elif lstfiles == None or len(lstfiles) <= 1:
            raise ValueError("The directory has " + str(len(lstfiles)) + " files!")
            #raise ValueError
            
        #the code is expecting a list
        elif type(lstfiles) != list: 
            raise TypeError("lstfiles paramter is not a list")
            
            
    def save_to_csv(self):
      
        if type(self.OutputDataFrame[0:3]) is pd.DataFrame and len(self.OutputDataFrame[0:3]) > 0: 
          
            if not exists(self.root + r'Data/Saved_Files'):
                makedirs(self.root + r'Data/Saved_Files')
            self.cd(self.root + r'Data/Saved_Files')
            
            if self.filter_column != None and self.filter_value != None:
                file_name = basename(self.concatenation_directory) + '[' + self.filter_column + '-' + \
                            self.filter_value + ']' +'(Output_' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')+ ').csv' 
            else:
                file_name = basename(self.concatenation_directory)  + '(Output_' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')+ ').csv'
            
            print('Saving File:', file_name)
            
            try:
                self.OutputDataFrame.to_csv(file_name, sep='\t', encoding='utf-8', index=False)
                saved_time = time() - self.start_time
                print('File saved with sucess!', "Total Expended Time:", saved_time, "\n")
                
            except Exception as e:
                return print('Error saving the file', e)
            
            if exists(file_name):
              del self.OutputDataFrame
            
    def output_filter(self, filter_column=None, filter_value=None):
      
        self.filter_column = filter_column
        self.filter_value = filter_value
        print('Filtering output...')
        self.OutputDataFrame = self.OutputDataFrame[self.OutputDataFrame[self.filter_column] == self.filter_value]                 
  