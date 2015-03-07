# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
from scrapy.http import FormRequest, Request
from scrapy.utils.response import open_in_browser
from stj.items import StjItem
import urlparse
import html2text
import re
from scrapy.shell import inspect_response
from datetime import datetime, timedelta

class STJSpider(BaseSpider):

    name = 'stj_num_acordaos'
    
    def nextDay( self, cur_date):
        y = int(cur_date[0:4])
        m = int(cur_date[4:6])
        d = int(cur_date[6:8])
        date = datetime( y,m,d)
        date = date + timedelta( days=1)
        d = str(date.day).zfill(2)
        m = str(date.month).zfill(2)
        y = str(date.year)
        return y+m+d
    
    def getParametersFromFile( self):
        print 'getting initial date and num previous acordaos from file'
        file = open("update_settings", 'r')
        prevIndex = file.readline() #first line should be the number of acordaos previously scraped
	prevFinalDate = file.readline()
        if prevIndex and prevFinalDate:
            self.iIndex = int( prevIndex)
            self.iDate  = self.nextDay( str( prevFinalDate))
	    return True
	else:
	    print 'cannot read settings file'
     	    return False

    def saveSearchInfo( self):
        print 'saving search parameters on file update_settings'
        file = open("update_settings", 'w')
	file.write( str(self.fIndex)+'\n')
	file.write( self.fDate)
	file.write( str(self.iIndex))
	file.close()

    def __init__ ( self, iDate, fDate, update):
        self.domain = 'stj.jus.br'
        self.start_urls = ["http://www.stj.jus.br/SCON/"]
	updateOK = 0
	if update is True:
	    updateOK = self.getParametersFromFile()
	if (not update) or (not updateOK):
            self.iDate = str(iDate).zfill(5)
	    self.iIndex = 0
	  #  self.iDate = raw_input('initial date: ')
	  #  self.fDate = raw_input('final date: ')
        self.fDate = str(fDate).zfill(5)
        self.fIndex = self.iIndex
	print 'starting to scrape from index '+ str(self.iIndex+1)
	print 'Acordaos from '+self.iDate+' to '+self.fDate
	print "\n\n\n"

    def parse(self, response):
        yield FormRequest.from_response(
            response,
            formname='frmConsulta',
            formdata={'livre':'(@DTDE >="'+self.iDate+'") E (@DTDE <="'+self.fDate+'")', 'b':'ACOR'},
            callback=self.parsePage
        )

    def parseItem( self, item ):
        return html2text.html2text( item)

    def orderSections( self, selectors, possHeader):
	sections = {}
	for sec in selectors:
	    header = self.parseItem(sec.xpath('./h4/text()').extract()[0])
	    for i, h in enumerate( possHeader):
	        if header.startswith( h):
	            sections[i] = sec
		    break
        return sections

    def parseSection( self, secSel, secTxtXpath, secRegex):     
        return re.match( secRegex, self.parseItem( secSel.xpath( secTxtXpath).extract()[0])).group(1)

    def parseDoc( self, doc):
	relator = dataJulg = dataPublic = ementa = decisao = notas = leis =''
	citacoes = []
	possSection = [
		'Data do Julg',	#0
		'Data da Publ', #1
		'Ementa',       #2
		'Ac',	        #3
		'Veja'          #4
	]

	sectionsSel =  doc.xpath('.//div[@class="paragrafoBRS"]')

	processoSection = sectionsSel[0].xpath('./div[@class="docTexto docRepetitivo"]/text()').extract()[0]
	processoSection = re.match( r"([a-zA-Z0-9 ]+)/ (..).*", self.parseItem(processoSection))
	acordaoId = self.getId( processoSection.group(1))
	uf        = processoSection.group(2)
	relator   = self.parseSection( sectionsSel[1], './pre/text()', r"Ministr.\W*([^\(]*).*")
	sections = self.orderSections( sectionsSel, possSection)
	dataJulg = self.parseSection( sections[0], './pre/span/text()', r"([\d\/]+)")
	if 1 in sections:
    	    dataPublic = sections[1].xpath( './pre/text()').extract()
	    dataPublic = re.search(r"(\d{2}\/\d{2}\/\d{4})" ,self.parseItem((''.join(dataPublic)))).group(1)
	ementa = self.parseItem( sections[2].xpath('./pre/text()').extract()[0])
	decisao= self.parseItem( sections[3].xpath( './pre/text()').extract()[0])
        if 4 in sections:
	    citacoes = sections[4].xpath('./pre/a/text()').extract()
	    citacoes = map(self.getId, citacoes)
#	print "--------------------------------------------------------------------------"
#	print 	acordaoId
#	print	uf
##		tipo+'\n'+
#	print 	relator
#	print	dataJulg
#	print 	dataPublic
#	print	ementa
#	print	decisao
#	print   citacoes
#	print "--------------------------------------------------------------------------"
	self.fIndex = self.fIndex + 1
        return StjItem(
            acordaoId   = acordaoId,
            uf          = uf,
            dataPublic  = dataPublic,
            dataJulg    = dataJulg,
            relator     = relator,
            ementa      = ementa,
            decisao     = decisao,
	    citacoes    = citacoes,
	    filename    = 'stj'+str(self.fIndex).zfill(6)
           #  indexacao   = indexacao,
           # legislacao  = legislacao,
          #  observacao  = observacao
        )

    def getId( self, txt):
	acId = txt.split(' no ')
	a = ''
	for i in reversed(acId):
	    a = a + i 
	return a

    def parsePage( self, response):
        print "\n\n\n\n"
	sel = Selector(response)
#	open_in_browser(response);
#        inspect_response(response)
        doclist = sel.xpath(
            '/html/body/div[@id="divprincipal"]/div[@class="minwidth"]/div[@id="idInternetBlocoEmpacotador"]/div[@class="incenter_interno"]'+
            '/div[@id="idDivContainer"]'+
            '/div[@id="idAreaBlocoExterno"]'+
            '/div[@id="idArea"]'+
            '/div[@id="corpopaginajurisprudencia"]'+
            '/div[@id="listadocumentos"]'+
	    '/div[@style="position: relative;"]')
        for doc in doclist:
	    yield self.parseDoc( doc)
#	self.virPageN = self.virPageN + 1 
        nextPage = sel.xpath('//*[@id="navegacao"]/a/img[@src="/recursos/imagens/tocn.gif"]')
	if nextPage:
	    yield Request( urlparse.urljoin('http://www.stj.jus.br/', nextPage.xpath('../@href').extract()[0]), callback=self.parsePage)
	else:
	  # r = raw_input('Save search parameters? (y/n):\n')
	  # print r
	   #if (r == "y"):
    	    self.saveSearchInfo()
