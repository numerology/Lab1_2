__author__ = 'Jiaxiao Zheng'

import json
import sys
import re
import urllib
from bs4 import BeautifulSoup

def contractAsJson(filename):
	soup = BeautifulSoup(open(filename), 'html.parser')
	jsonQuoteData = {
		"currPrice" : 0.0,
		"dateUrls" : [],
		"optionQuotes" : []
	}
	#the class name for current price is `time_rtq_ticker`
	#we don't have complete dateUrls, the complete version is "http://finance.yahoo.com/q/op?s=AAPL&amp;m=2014-08",
	# what we can find: "/q/op?s=AAPL&amp;m=2014-08" under the <a href = ></a>
	# need regex
	currPrice = soup.find_all('span', class_ = 'time_rtq_ticker')[0].contents[0].contents[0]
	jsonQuoteData['currPrice'] = float(currPrice)

	#decide the abbr for company name
	company_full = soup.find_all('div', class_ = 'title')[0].contents[0].contents[0]
	company_abbr = company_full.split('(')[1].split(')')[0]

	#find pattern /q/op or s ?s=company_abbr&amp;m=
	key_str = '\/q\/o[ps]?\?s\=' + str(company_abbr)+'\&m\='
	regex = re.compile(key_str)
	url_list = soup.find_all('a', href = regex)
	for url in url_list:
		jsonQuoteData['dateUrls'].append('http://finance.yahoo.com' + str(url['href']).replace('&', '&amp;'))


	# table contents are tagged by 'yfnc_tabledata1' or 'yfnc_h', based on the background color
	# but the last line with such keyword is empty
	key_str = 'yfnc_((h)|(tabledata1))'
	regex = re.compile(key_str)
	data_list = soup.find_all('td' , class_ = regex)

	tmp = dict()

	for idx in range(0,len(data_list)-1):


		if idx%8 == 0:
			tmp['Strike'] = data_list[idx].a.strong.contents[0]
		elif idx%8 == 1:
			#have to count backward
			code = data_list[idx].a.contents[0]
			tmp['Symbol'] = code[:-15]
			tmp['Date'] = code[-15:-9]
			tmp['Type'] = code[-9:-8]
		elif idx%8 == 2:
			# maybe NA
			if data_list[idx].contents[0] == 'N/A':
				tmp['Last'] = 'N/A'
			else:
				tmp['Last'] = data_list[idx].b.contents[0]
		elif idx%8 == 3: #why there is a space?
			tmp['Change'] = ' '+data_list[idx].span.b.contents[0]
		elif idx%8 == 4:
			tmp['Bid'] = data_list[idx].contents[0]
		elif idx%8 == 5:
			tmp['Ask'] = data_list[idx].contents[0]
		elif idx%8 == 6:
			tmp['Vol'] = data_list[idx].contents[0]
		elif idx%8 == 7:
			tmp['Open'] = data_list[idx].contents[0]
			jsonQuoteData['optionQuotes'].append(tmp)
			tmp = dict()

	jsonQuoteData['optionQuotes'].sort(key = lambda elem: -int(str(elem['Open']).replace(',' , '')))
	jsonQuoteData = json.dumps(jsonQuoteData)


	return jsonQuoteData









