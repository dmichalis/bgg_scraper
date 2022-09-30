import numpy as np
import pandas as pd
import csv
from bs4 import BeautifulSoup

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")
from class_boardgames import Boardgames


#Ask whether a new csv file should be used
while True:
    answer = input('Do you want to create a new csv file? [Y/n] ')
    if answer == 'Y' or answer == 'n':
        break

if answer == 'Y':
    start = 1
    #write csv file    
    f = open('Board_games.csv', 'w', encoding='UTF8', newline='')
    header = ['Name', 'Board game url', 'BGG Rating', 'User rating', 'Total reviews', 'Max # players', 
         'Optimal # players', 'Min playing time', 'Max playing time', 'Weight/5', 'Min price', 'Skroutz url']
    wr = csv.writer(f)
    wr.writerow(header)
else:
    start = int(input('From which line should the csv start? The number must be in the range [3-3000]')) - 2 #must have at least 1 element and remove header line
    df = pd.read_csv('Board_games.csv')

#initialize necessary parameters
flag = int(input('How many board games do you want to retrieve from the list? '))
blank_count = (start-1)//15  #each page contains 6 blank lines per 15 board games
page = (start-1)//100
count = (start-1)+blank_count
count_page = count%100
url_count = 0
url = []
url.append('https://boardgamegeek.com/browse/boardgame/page/'+str(page+1)+'?sort=rank')

#Get the corresponding data
while count < (start+flag-1)+blank_count:
    #retrieve the corresponding page from bgg site; each page contains 100 games
    url.append('https://boardgamegeek.com/browse/boardgame/page/'+str(page+1)+'?sort=rank')
    
    html = requests.get(url[page])
    soup = BeautifulSoup(html.content, 'html.parser')
    results = soup('tr')[1:] #ignore the first entry
    print(count, page, count_page, blank_count)
    
    #-----------retrieve data for each board game----------------------
    try:
        game_name = results[count_page].find(class_ = 'primary').text
    except:
        count += 1
        continue

    #get the shop url
    init_url = results[count_page].find(class_ = 'primary')['href']
    bgg_url = 'https://boardgamegeek.com'+ init_url
    #
    #get the rating of each game
    res_ratings = results[count_page].find_all(class_ = 'collection_bggrating')
    bgg_rating = float(res_ratings[0].text.split()[0])
    user_rating = float(res_ratings[1].text.split()[0])
    votes = int(res_ratings[2].text.split()[0])
    
    #open bgg_url and retrieve extra attributes
    p = Boardgames(bgg_url)
    max_p = p._maxplayers()
    opt_p = p._players()
    min_t, max_t = p._playingtime()
    dif = p._weight()
    
    #Perform a google search
    query = f'{game_name}' + ' ' + 'skroutz'
    try:
        first_option = True
        for web_url in search(query, tld="co.in", num=2, stop=2, pause=2):
            if 'keyphrase' not in web_url and first_option == True:
                first_option = False
                skroutz_url = web_url
                
        #get the corresponding price from skroutz.gr
        driver = webdriver.Chrome()
        driver.get(skroutz_url)
        html = requests.get(skroutz_url)
        price = driver.find_element(By.CLASS_NAME, 'dominant-price').text.split()[0].replace(',' , '.')        
    except:
        price = '-'
        skroutz_url = '-'
    #-----------------------------------------------------------------------
      
    #------------------Print the results in the csv file--------------------
    if start == 1:
        wr.writerow([game_name, bgg_url, bgg_rating, user_rating, votes, max_p,
        opt_p, min_t, max_t, dif, price, skroutz_url])    
    else:
        new_row = pd.Series(data={'Name':game_name , 'Board game url':bgg_url, 'BGG Rating':bgg_rating, 
                  'User rating':user_rating, 'Total reviews':votes, 'Max # players':max_p, 
                  'Optimal # players':opt_p, 'Min playing time':min_t, 'Max playing time':max_t, 
                  'Weight/5':dif, 'Min price':price, 'Skroutz url':skroutz_url})
        df = df.append(new_row, ignore_index=True)
    #----------------------------------------------------------------------  

    count += 1
    page = count//100
    count_page = count%100  #when the index surpasses 100, it resets because each page contains 100 board games
    blank_count = count_page//15

#Replace the existing csv 
if start > 1:
    df.to_csv('Board_games.csv', index=False)
