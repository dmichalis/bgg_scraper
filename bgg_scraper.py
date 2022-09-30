import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import csv
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
header = ['Name', 'Board game url', 'BGG Rating', 'User rating', 'Total reviews', 'Max # players', 
         'Optimal # players', 'Min playing time', 'Max playing time', 'Weight/5', 'Min price', 'Skroutz url']

if answer == 'Y':
    start = 1
    #write csv file    
    f = open('Board_games.csv', 'w', encoding='UTF8', newline='')
    wr = csv.writer(f)
    wr.writerow(header)
else:
    start = int(input('From which line should the csv start? The number must be in the range [3-3000] ')) -1 #must have at least 1 element and remove header line
    df = pd.read_csv('Board_games.csv')

#initialize necessary parameters
flag = int(input('How many board games do you want to retrieve from the list? '))
blank_count = start//15  #each page contains 6 blank lines per 15 board games
page = start//100
count = start+blank_count
count_page = start%100

#Get the corresponding data
while count < (start+flag)+blank_count:
    #retrieve the corresponding page from bgg site; each page contains 100 games
    url = 'https://boardgamegeek.com/browse/boardgame/page/'+str(page+1)+'?sort=rank'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    results = soup('tr')[1:] #ignore the first entry
    
    #-----------retrieve data for each board game----------------------
    #get the shop url
    game_name = results[count_page+blank_count-1].find(class_ = 'primary').text
    init_url = results[count_page+blank_count-1].find(class_ = 'primary')['href']
    bgg_url = 'https://boardgamegeek.com'+ init_url
    #
    #get the rating of each game
    res_ratings = results[count_page+blank_count-1].find_all(class_ = 'collection_bggrating')
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
        print(df['Name'].values[count_page+blank_count-1])
        if len(df) > count_page: #update the list
            new_row = [game_name, bgg_url, bgg_rating, user_rating, votes, max_p, opt_p, min_t, max_t, dif, price, skroutz_url]
            for i in range(12):
                df[header[i]].values[count_page+blank_count-1] = new_row[i]
        else:
            new_row = pd.Series(data={'Name':game_name , 'Board game url':bgg_url, 'BGG Rating':bgg_rating, 
                  'User rating':user_rating, 'Total reviews':votes, 'Max # players':max_p, 
                  'Optimal # players':opt_p, 'Min playing time':min_t, 'Max playing time':max_t, 
                  'Weight/5':dif, 'Min price':price, 'Skroutz url':skroutz_url}, name=str(count_page))

            df = df.append(new_row)
    #----------------------------------------------------------------------  
   
    count += 1
    blank_count = count_page//15
    if  count_page%15 != 0:
        count_page = (count-blank_count)%100  #when the index surpasses 100, it resets because each page contains 100 board games
    else:
        count += 1
        count_page += 1

    page = count_page//100

#Replace the existing csv
if start > 1:
    df.to_csv('Board_games.csv', index=False)
    
    
