from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find('div', attrs={'class':'lister-list'}) 
    #tr = table.find_all(___) 
    test2 = table.find_all('div', attrs={'lister-item-content'})
    temp = [] #initiating a tuple

    for i in range(0, len(test2)):
        test2 = table.find_all('div', attrs={'lister-item-content'})[i]
        #Get Title
        title = test2.find_all('h3')[0].find_all('a')[0].text
        #Get IMDB Rating
        imdb_rating = test2.find_all('div','inline-block ratings-imdb-rating')[0].find_all('strong')[0].text
        #Get votes
        votes = test2.find_all('p','sort-num_votes-visible')[0].find_all('span')[1].text
        #Get Metascore
        try:metascore = test2.find_all('div','inline-block ratings-metascore')[0].find_all('span')[0].text.strip()
        except IndexError:metascore = 0





        temp.append((title,imdb_rating, metascore, votes)) #append the needed information 
    
    #temp = temp[::-1] #remove the header

    imdb = pd.DataFrame(temp, columns = ('title','imdb_rating', 'metascore', 'votes')) #creating the dataframe
   #data wranggling -  try to change the data type to right data type
    imdb['metascore'] = imdb['metascore'].astype('int')
    imdb['imdb_rating'] = imdb['imdb_rating'].astype('float')
    imdb['votes'] = imdb['votes'].replace(
    '[^\d.]+', '', 
    regex=True)
    imdb['votes'] = imdb['votes'].astype('int')
   #end of data wranggling
    imdb.set_index('title', inplace=True)
    imdb = imdb.sort_values(by='votes', ascending=False).head(7)
    imdb
    return imdb

@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,5),dpi=300)
    
    df['votes'].plot(kind= 'barh')
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
