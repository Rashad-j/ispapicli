import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path


class Scrap:
    def __init__(self, URL):
        self.mainURL = URL

    # recursive function
    def getURLs(self, urls):
        # urls to return
        Allurls = []
        # parse url
        for url in urls:
            if(self.checkUrlType(url) == 'file'):
                Allurls.append(url)
                print('url found: ' + url)
                # create the command here
            else:
                # it is a directory
                # get all links in this directory
                newLinks = self.getPageURLs(url)
                # for each link, call it by the function itself
                for newlink in newLinks:
                    Allurls.extend(self.getURLs([newlink]))
        return Allurls

    def getPageURLs(self, url):
        # urls in a single page to return
        urls = []
        page = requests.get(url)
        # get page download status, 200 is success
        statusCode = page.status_code
        if statusCode == 200:
            # get the page content
            src = page.content
            # parse HTML content, create bs4 object
            html = BeautifulSoup(src, 'html.parser')
            # get table body
            tbody = html.table.tbody
            # get tr
            rows = tbody.find_all('tr', attrs={'class': 'js-navigation-item'})
            for row in rows:
                # href = row.a['js-navigation-open']
                td = row.find('td', attrs={'class': 'content'})
                href = td.find('a', attrs={'class': 'js-navigation-open'})
                # add the url to the urls
                urlLink = 'https://github.com/' + href.get('href')
                urls.append(urlLink)
            # return urls
            return urls
        else:
            raise Exception(
                "Page couldn't loaded. Status code: " + str(statusCode))

    def checkUrlType(self, url):
        if url.endswith('.md'):
            return 'file'
        else:
            return 'directory'

    def getParsedPage(self, url):
        try:
            page = requests.get(url)
            # get page download status, 200 is success
            statusCode = page.status_code
            # get the page content
            src = page.content
            # parse HTML content, create bs4 object
            html = BeautifulSoup(src, 'html.parser')
            # get only the command description element
            article = html.article
            # table of parametrs
            table = article.table
            return article, table
        except:
            return "Couldn't parse page: " + url

    def getCommandName(self, article):
        # since there is only one h1 element in article block, return it
        return article.h1.text

    # description of the command
    def getCommandDescription(self, article):
        # 1st p is the description
        # adding exception for webely
        try:
            desc = article.find_all('p')
            return desc[0].text
        except:
            return ' '
    # get comman avaiablity

    def getCommandAvailability(self, article):
        # 2nd p is the description
        try:
            ava = article.find_all('p')
            return ava[1].text
        except:
            return ' '

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

    def getCommandExample(self, article):
        pass

    def getResponseExample(self, article):
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
        p = Path('../commands/'+commandName+'.json')
        with p.open('w') as outfile:
            json.dump(data, outfile)
            outfile.close
        print('Command file created: ', p)

    def getCommandData(self, article, table):
        data = {}
        data['command'] = self.getCommandName(article)
        data['description'] = self.getCommandDescription(article)
        data['availability'] = self.getCommandAvailability(article)
        data['paramaters'] = self.getCommandParameters(table)
        return data


if __name__ == "__main__":
    gitHubURL = 'https://github.com/hexonet/hexonet-api-documentation/tree/master/API'
    try:
        scrap = Scrap(gitHubURL)
        urls = scrap.getURLs([gitHubURL])
        for url in urls:
            try:
                article, table = scrap.getParsedPage(url)
                commandName = scrap.getCommandName(article)
                data = scrap.getCommandData(article, table)
                scrap.dumpCommandToFile(commandName, data)
            except Exception as e:
                print("Couldn't extract command because documentation differs in URL: " +
                      url+" \nReason: " + str(e))
        print('\n Commands created successfully!')
    except Exception as e:
        print("Process stopped due to: " + str(e))
