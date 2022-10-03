from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'lister list detail sub-list'})
jumlah = table.find_all('h3', attrs={'class':'lister-item-header'})

jumlah_row = len(jumlah)

temp = [] #initiating a list 

for i in range(0, jumlah_row):
    #mendapatkan judul
    title = table.find_all('h3', attrs={'class':'lister-item-header'})[i].find('a').text
    
    #mendapatkan imdb
    rating_imdb = table.find_all('div', attrs={'class':'inline-block ratings-imdb-rating'})[i].find('strong').text
    
    #mendapatkan metascore
    metascore = table.find_all('div', attrs={'class':'ratings-bar'})[i]
    ali = metascore.find('div', attrs={'class':'inline-block ratings-metascore'})
    if (ali is not None):
        skor_ali=ali.find('span').text.strip()
    else:
        skor_ali=0
        
    #mendapatkan total vote
    total_vote = table.find_all('div', attrs={'class':'ratings-bar'})[i].find('meta', attrs={'itemprop':'ratingCount'})['content']
    
    temp.append((title, rating_imdb, skor_ali, total_vote)) 


#change into dataframe
df = pd.DataFrame(temp, columns=('Title', 'IMDB_Rating', 'Metascore','Total_Vote'))

#insert data wrangling here
df['IMDB_Rating'] = df['IMDB_Rating'].astype('float64')
df[['Metascore', 'Total_Vote']] = df[['Metascore', 'Total_Vote']].astype('int64')
df = df.set_index('Title')
plot_2 = df.drop(['IMDB_Rating','Metascore'], axis=1)
vote_plot = plot_2.sort_values(by='Total_Vote', ascending=True)

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Total_Vote"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = vote_plot.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)