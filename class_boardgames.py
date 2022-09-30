import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class Boardgames(object):
    #Retrieve data from the site of each board game#

    def __init__(self, url): 
        self.driver = webdriver.Chrome() 
        self.driver.get(url)
        html = requests.get(url)   
    
    #----------Get the max number of players--------------
    def _maxplayers(self):
        try: #if one best option is available
            max_players = int(self.driver.find_element(By.XPATH, "//div[@class='gameplay-item-primary']/span").text)
        except:
            max_players = int(self.driver.find_element(By.XPATH, "//div[@class='gameplay-item-primary']/span").text.split('–')[1])

        return max_players
    #---------------------------------------------------    
    
    #----------Get the best and suggested number of players--------------
    def _players(self):
        elem1 = self.driver.find_element(By.XPATH, "//div[@class='gameplay-item-secondary']").text.split('Best:')[1]   
        try: #if one best option is available
            best = int(elem1)
        except:
            try:
                best = int(elem1.split('–')[1])
            except:
                best = int(elem1.split(',')[1])
                
        return best
    #--------------------------------------------------- 

    #----------Get the average playing time--------------
    def _playingtime(self):
        try: #if there is a range 
            elem2 = self.driver.find_element(By.XPATH, "//li[2]/div[@class='gameplay-item-primary']/span[1]").text.split('–')
            min_time = int(elem2[0])
            max_time = int(elem2[1].split()[0])
        except:
            min_time = 0
            max_time = int(self.driver.find_element(By.XPATH, "//li[2]/div[@class='gameplay-item-primary']/span[1]").text.split()[0])

        return min_time, max_time    
    #---------------------------------------------------

    
    #----------Get the difficulty--------------
    def _weight(self):
        weight = float(self.driver.find_element(By.XPATH, "//li[4]/div[@class='gameplay-item-primary']").text.split()[1])
    
        return weight
    #---------------------------------------------------

    def __del__(self):
        self.driver.close() 
