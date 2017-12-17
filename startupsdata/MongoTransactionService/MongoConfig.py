'''
Created on 14-Dec-2017

@author: ev71
'''
from pymongo import MongoClient


class MongoService(object):
    '''
    classdocs
    '''
    mongoUrl='localhost:27017'
    client=''
    db=''

    def __init__(self,databasename):
        client = MongoClient("mongodb://"+self.mongoUrl)
        self.db=client[databasename]
        
    def save(self,data):       
        self.db.startups.insert_one(data)
        
    def find(self,query,collectionName):       
        return self.db[collectionName].find(query)
        
    def saveInCollection(self,data,collectionName):
        data["_id"]=data["name"]
        self.db[collectionName].save(data)
        
        