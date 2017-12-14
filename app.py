from __future__ import print_function

import json

from bs4 import BeautifulSoup
from flask import Flask
import requests

from model import SearchDataResult
from model.SearchDataResult import SearchData


try:
    from types import SimpleNamespace as Namespace
except ImportError:
    from argparse import Namespace

app = Flask(__name__)

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, SearchDataResult):
            return super(MyEncoder, self).default(obj)

        return obj.__dict__
@app.route("/")
def hello():
    #j = "{    \"ids\": [        2282346,        2084485,        2130318,        2480268,        2480931,        3365754,        3244326,        3322647,        3394926,        656451,        650830,        652436,        652259,        658177,        48804,        658877,        659486,        609281,        609421,        655517    ],    \"total\": 3547121,    \"page\": 1,    \"sort\": \"signal\",    \"new\": false,    \"hexdigest\": \"dff2133a8b867e9078b04c66aed28c9f63ba6516\"}"
    searchDataFromAngellist=''
    for i in range(1, 10):
        x=getCompanyidsperpage(i)
        param = "?"
        for id in x.ids:
            param=param+"ids[]="+id.__str__()+"&"
        param = param+"sort="+"\""+x.sort+"&"
        param = param+"new="+x.new.__str__()+"&"
        param = param+"hexdigest="+x.hexdigest
        searchResult=requests.get("https://angel.co/companies/startups"+param)
        #data=json.loads(searchResult.text, object_class:SearchData)
        companyList=json.loads(searchResult.text, object_hook=lambda d: Namespace(**d))
        searchDataFromAngellist=searchDataFromAngellist+companyList.html
    soup = BeautifulSoup(searchDataFromAngellist, 'html.parser')
    for link in soup.find_all('div',attrs={"class": "base startup"}):
        tag=link
        for sibling in tag.find_all(has_class_but_no_id):
            print("Company Name:",sibling.string)
        for sibling in tag.find_all('div',attrs={"class":"value"}):
            print(sibling.parent["data-column"],":", sibling.string)
    return soup.prettify()

def has_class_but_no_id(tag):
    return tag.name=='a' and tag.has_attr("class") and 'startup-link' in tag["class"] and not tag.has_attr('title')

def getCompanyidsperpage(i):
    head = {"X-Requested-With":"XMLHttpRequest"}
    params = {"sort":"signal","page":i}
    searchResult=requests.post("https://angel.co/company_filters/search_data",params=params,headers=head)
    data = SearchData(searchResult.text)
    print(data.ids)
    return data
#json.loads(searchResult.text, object_hook=lambda d: Namespace(**d))
  
if __name__ == "__main__":
    app.run(port=8080)