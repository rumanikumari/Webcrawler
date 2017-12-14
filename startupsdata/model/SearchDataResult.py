'''
Created on 14-Dec-2017

@author: ev71
'''
import json

class SearchData:
    '''
    classdocs
    '''
    ids=[]
    total=''
    page=''
    sort=''
    new=''
    hexdigest=''

    def __init__(self, params):
        self.__dict__ = json.loads(params)
        