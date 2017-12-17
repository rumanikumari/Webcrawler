from __future__ import print_function

import json

from bs4 import BeautifulSoup
from flask import Flask
from flask import request
import requests

from model import SearchDataResult
from model.SearchDataResult import SearchData
from MongoTransactionService.MongoConfig import MongoService
from model.Company import CompanyData
from _ast import Param
from werkzeug import MultiDict


try:
    from types import SimpleNamespace as Namespace
except ImportError:
    from argparse import Namespace

app = Flask(__name__)

MongoServiceObject=MongoService("test")
headersForClearbit={"Authorization":"Bearer sk_28facfab921cfd1bebc9e26558ca5093"}

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, SearchDataResult):
            return super(MyEncoder, self).default(obj)

        return obj.__dict__
@app.route("/company",methods=['GET'])
def hello():
    companyInfoList=[]
    #print(request.args.getlist("filter_data[company_types][]"))
    #for item in request.args.iteritems(multi=True):
    #    print(item[0])
    for i in range(1,20):
        x=getCompanyidsperpage(i,request.args)
        param = "?"
        for id in x.ids:
            param=param+"ids[]="+id.__str__()+"&"
        param = param+"sort="+x.sort+"&"
        param = param+"new="+x.new.__str__()+"&"
        param = param+"hexdigest="+x.hexdigest
        searchResult=requests.get("https://angel.co/companies/startups"+param)
        companyList=json.loads(searchResult.text, object_hook=lambda d: Namespace(**d))
        companyInfoList.extend(parseHtmlToGetData(companyList.html))
    return json.dumps(companyInfoList)

@app.route("/populateDomain")
def populateDomain():
    mongoResult=MongoServiceObject.find({"website": None},"CompanyDetails")
    companyInfoList=[]
    for doc in mongoResult:
        companyInfoList.append(doc)
        if not doc.has_key("website") or doc["website"] is None:
            clearTripResponse=requests.get("https://company.clearbit.com/v1/domains/find",params={"name":doc["name"]},headers=headersForClearbit)                      
            domainName=json.loads(clearTripResponse.text, object_hook=lambda d: dict(**d))
            doc["website"]=None if domainName.has_key("error") else domainName["domain"]
            MongoServiceObject.saveInCollection(doc,"CompanyDetails")
    return json.dumps(companyInfoList)

def populateFromLinkedIn(companyName):
    clearTripResponse=requests.get("https://www.linkedin.com/company/"+companyName+"/")                      
    soup = BeautifulSoup(clearTripResponse, 'html.parser')
    aboutCompany=soup.find('code',attrs={"id":"stream-about-section-embed-id-content"}).string.json()
    return aboutCompany["website"] if aboutCompany.has_key("website") else None
    
    

def parseHtmlToGetData(data):
    soup = BeautifulSoup(data, 'html.parser')
    companyInfoList=[]
    for link in soup.find_all('div',attrs={"class": "base startup"}):
        companyInfo=CompanyData()
        tag=link
        for sibling in tag.find_all(has_class_but_no_id):
            companyInfo.name=sibling.string
        for sibling in tag.find_all('div',class_="column hidden_column joined"):
            for inner in sibling.find_all('div',attrs={"class":"value"}):
                companyInfo.joinedOn=inner.string
        for sibling in tag.find_all('div',attrs={"class":"column hidden_column location"}):
            for inner in sibling.find_all('a'):
                companyInfo.location=inner.string
        for sibling in tag.find_all('div',attrs={"class":"column hidden_column market"}):
            for inner in sibling.find_all('a'):
                companyInfo.market=inner.string
        for sibling in tag.find_all('div',attrs={"class":"column hidden_column website"}):
            for inner in sibling.find_all('a'):
                companyInfo.website=inner.string
            if companyInfo.website is '':
                clearTripResponse=requests.get("https://company.clearbit.com/v1/domains/find",params={"name":companyInfo.name},headers=headersForClearbit)                      
                domainName=json.loads(clearTripResponse.text, object_hook=lambda d: dict(**d))
                companyInfo.website=None if domainName.has_key("error") else domainName["domain"]
        for sibling in tag.find_all('div',attrs={"class":"column hidden_column company_size"}):
            for inner in sibling.find_all('div',attrs={"class":"value"}):
                companyInfo.companySize=inner.string
        for sibling in tag.find_all('div',attrs={"class":"column hidden_column raised"}):
            for inner in sibling.find_all('div',attrs={"class":"value"}):
                companyInfo.totalRaised=inner.string
        companyInfoList.append(companyInfo.__dict__)
        MongoServiceObject.saveInCollection(companyInfo.__dict__,"CompanyDetails")
    return companyInfoList
    

def has_class_but_no_id(tag):
    return tag.name=='a' and tag.has_attr("class") and 'startup-link' in tag["class"] and not tag.has_attr('title')

def getCompanyidsperpage(i,requestparams):
    head = {"X-Requested-With":"XMLHttpRequest"}
    params = {"sort":"signal","page":i}
    for item in requestparams.iteritems(multi=True): 
        params[item[0]]=item[1]
    #,"filter_data[keywords]":"Savory"
    searchResult=requests.post("https://angel.co/company_filters/search_data",params=params,headers=head)
    return SearchData(searchResult.text)
  
if __name__ == "__main__":
    app.run(port=8080)