import time
import requests
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class CyberLeninka:
    def init_driver(self):
        options = Options()
        # options.add_experimental_option("detach", True)
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument(f"user-agent={UserAgent(use_external_data=True).random}")
        # options.add_argument("--start-maximized")
        options.add_argument("--headless")
        s = Service(str(Path.cwd() / 'yandexdriver.exe'))
        self.browser = webdriver.Chrome(service=s, options=options)

    def get_main_page(self, i):
        url = f"https://cyberleninka.ru/article/c/mathematics/{i}"
        self.browser.get(url)
        WebDriverWait(self.browser, 200).until(EC.title_contains("Темы научных статей по математике из каталога электронной библиотеки КиберЛенинка"))

    def get_element_web_driver_wait(self, selector, by=By.CSS_SELECTOR, delay=20):
        return WebDriverWait(self.browser, delay).until(EC.visibility_of_element_located((by, selector)))
    
    
    def parce_article_page(self, article_url):
        url = "https://cyberleninka.ru" + article_url
        # page = requests.get(url)
        # soup = BeautifulSoup(page.text, "html.parser")
        self.browser.get(url)
        
        name_selector = "#body > div.content > div > span > div:nth-child(2) > h1 > i"
        author_selector = "#body > div.content > div > span > div:nth-child(2) > div.infoblock.authors.visible > div:nth-child(1) > ul > li"
        journal_selector = "#body > div.content > div > span > div:nth-child(2) > div:nth-child(6) > div.half > span > a"
        year_selector = "#body > div.content > div > span > div:nth-child(2) > div:nth-child(6) > div.half > div.labels > div.label.year > time"
        text_selector = "#body > div.content > div > span > div:nth-child(2) > div:nth-child(14) > div > div"
        
        name = self.get_element_web_driver_wait(name_selector).text
        author = self.get_element_web_driver_wait(author_selector).text
        journal = self.get_element_web_driver_wait(journal_selector).text
        year = self.get_element_web_driver_wait(year_selector).text
        text = self.get_element_web_driver_wait(text_selector).text
        
        return name, author, journal, year, text
        

    def parce_page(self):
        link_element = "#body > div.content > div > div.visible > div > ul"
        link_html = self.get_element_web_driver_wait(link_element).get_attribute('innerHTML')
        soup = BeautifulSoup(link_html, 'html.parser')
        a_link = soup.find_all("a", href=True)
        
        path = Path("dataset.csv")
        
        if path.is_file():
            base_dataset = pd.read_csv(path)
        else:
            base_dataset = pd.DataFrame(columns=["Название", "Автор", "Журнал", "Год", "Текст"])
        
        names, authors, journals, years, texts = [], [], [], [], []
        for el in a_link:
            try:
                name, author, journal, year, text = self.parce_article_page(el["href"])
                names.append(name)
                authors.append(author)
                journals.append(journal)
                years.append(year)
                texts.append(text)
            except Exception as e:
                print(e)
            
        dataset = pd.DataFrame({
            "Название": names,
            "Автор": authors,
            "Журнал": journals,
            "Год": years,
            "Текст": texts,
        })
        
        pd.concat([base_dataset, dataset]).to_csv(path)


    def run(self, n_pages):
        self.init_driver()
        
        for i in range(n_pages):
            self.get_main_page(i)
            self.parce_page()
    

if __name__ == "__main__":
    CyberLeninka().run(1)
