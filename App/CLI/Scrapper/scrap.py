import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path


class Scrap:
    def __init__(self):
        # GitHub URL
        self.url = 'https://github.com/hexonet/hexonet-api-documentation/blob/master/API/DOMAIN/ADDON/QUERYDOMAINADDONLIST.md'
        self.page = requests.get(self.url)
        # get page download status, 200 is success
        self.statusCode = self.page.status_code
        self.headers = self.page.headers
        # get the page content
        self.src = self.page.content
        # parse HTML content, create bs4 object
        self.results = BeautifulSoup(self.src, 'html.parser')
        # get only the command description element
        self.article = self.results.article
        # table of parametrs
        self.table = self.article.table

    def getCommandName(self):
        # since there is only one h1 element in article block, return it
        return self.article.h1.text

    # description of the command
    def getCommandDescription(self):
        # 1st p is the description
        desc = self.article.find_all('p')
        return desc[0].text

    # get comman avaiablity
    def getCommandAvailability(self):
        # 2nd p is the description
        ava = self.article.find_all('p')
        return ava[1].text

    # allowed parameters
    def getCommandParameters(self, table):
        # get columns names
        headers = self.getTableHeaders(table)
        params = []
        param = {}
        tableBody = table.tbody
        rows = tableBody.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            for i in range(0, len(cols)):
                param[headers[i]] = cols[i].text
            # append params
            params.append(param)
            param = {}
        return params

    def getCommandExample(self):
        pass

    def getResponseExample(self):
        pass

    def getTableHeaders(self, table):
        tableHead = table.thead
        row = tableHead.tr
        cols = row.find_all('th')
        data = []
        # get text only
        for col in cols:
            data.append(col.text)
        return data

    def dumpCommandToFile(self, commandName, data):
        # if command file does not exist, create it and dump
        p = Path('../Commands/'+commandName+'.json')
        with p.open('w') as outfile:
            json.dump(data, outfile)
            outfile.close

    def getCommandData(self, table):
        data = {}
        data['command'] = self.getCommandName()
        data['description'] = self.getCommandDescription()
        data['availability'] = self.getCommandAvailability()
        data['paramaters'] = self.getCommandParameters(table)
        return data


if __name__ == "__main__":
    scrap = Scrap()
    # print(scrap.getCommandName())
    # print(scrap.getCommandDescription())
    # print(scrap.getCommandParameters(scrap.article.table))
    # print(scrap.getCommandAvailability())
    # print(scrap.getTableHeaders())
    table = scrap.article.table
    data = scrap.getCommandData(table)
    print(data)
    commandName = scrap.getCommandName()
    print(scrap.dumpCommandToFile(commandName, data))
