from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import sqlite3 as lite
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm


url = "http://web.archive.org/web/20110514112442/http://unstats.un.org/unsd/demographic/products/socind/education.htm"
con = lite.connect('countrydata.db')
cur = con.cursor()
r = requests.get(url)
soup = BeautifulSoup(r.content)   
table = soup('table')[6]
datafields = table('td')[3]

countrylist = []
yearlist = []
malelist = []
femalelist = []
combinedlist = []

with con:
    cur.execute("DROP TABLE IF EXISTS education;")
    cur.execute('CREATE TABLE education (country_name STR PRIMARY KEY, year INT, male INT, female INT, combined INT)')
    cur.execute("DROP TABLE IF EXISTS gdp;")
    cur.execute('CREATE TABLE gdp (country_name STR, _1999 FLOAT, _2000 FLOAT, _2001 FLOAT, _2002 FLOAT, _2003 FLOAT, _2004 FLOAT, _2005 FLOAT, _2006 FLOAT, _2007 FLOAT, _2008 FLOAT, _2009 FLOAT, _2010 FLOAT)')

for i in range(183):
	if i == 0:
		countrylist.append(datafields('td')[11].get_text())
		yearlist.append(datafields('td')[12].get_text())
		malelist.append(datafields('td')[15].get_text())
		femalelist.append(datafields('td')[18].get_text())
		combinedlist.append(datafields('td')[21].get_text())
	else:
		countrylist.append(datafields('td')[(11+(12*i))].get_text())
		yearlist.append(datafields('td')[(12+(12*i))].get_text())
		malelist.append(datafields('td')[(15+(12*i))].get_text())
		femalelist.append(datafields('td')[(18+(12*i))].get_text())
		combinedlist.append(datafields('td')[(21+(12*i))].get_text())


for a, b, c, d, e in zip(countrylist, yearlist, malelist, femalelist, combinedlist):
	cur.execute('INSERT into education values (?,?,?,?,?)', (a, b, c, d, e,))

with open('ny.gdp.mktp.cd_Indicator_en_csv_v2.csv','rU') as inputFile:
    next(inputFile) 
    header = next(inputFile)
    inputReader = csv.reader(inputFile)
    for line in inputReader:
    	with con:
			cur.execute('INSERT INTO gdp (country_name, _1999, _2000, _2001, _2002, _2003, _2004, _2005, _2006, _2007, _2008, _2009, _2010) VALUES ("' + (line[0].lstrip()) + '","' + '","'.join(line[43:-4]) + '");')
			
df1 = pd.read_sql_query("SELECT * FROM gdp" ,con,index_col='country_name')
df2 = pd.read_sql_query("SELECT * FROM education" ,con,index_col='country_name') 
df = pd.concat([df1, df2], axis=1, join='inner')

gdplist = []
for i in range(0, df.shape[0]):
	gdplist.append(df.irow(i)['_' + str(df.irow(i)['year'])])
	
df['gdpyear'] = gdplist	
df = df[df.gdpyear != ""]
df['gdpyear'] = df[['gdpyear']].convert_objects(convert_numeric=True)
df['combinedlog'] = np.exp(df['combined'])

df['intercept'] = float(1.0)
X = df[['intercept', 'gdpyear']]
y = df['combinedlog']
X = sm.add_constant(X)
est = sm.OLS(y, X).fit()
print(est.summary())
model1 = sm.OLS(df['combinedlog'], df[['intercept', 'gdpyear']])
res1 = model1.fit()
print res1.summary()





	


