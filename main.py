from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm


class CyberLeninka:
    def init_driver(self):
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--headless")
        s = Service(str(Path.cwd() / 'yandexdriver.exe'))
        self.browser = webdriver.Chrome(service=s, options=options)

    def get_page(self, i):
        url = f"https://cyberleninka.ru/article/c/mathematics/{i}"
        self.browser.get(url)
        WebDriverWait(self.browser, 200).until(
            EC.title_contains("Темы научных статей по математике из каталога электронной библиотеки КиберЛенинка"))

    def get_element_web_driver_wait(self, selector, by=By.CSS_SELECTOR, delay=10):
        return WebDriverWait(self.browser, delay).until(EC.visibility_of_element_located((by, selector)))

    def parce_article_page(self, article_url):
        url = "https://cyberleninka.ru" + article_url

        self.browser.get(url)
        html = self.get_element_web_driver_wait("#body > div.content > div > span > div:nth-child(2)").get_attribute(
            'innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        infoblock = soup.find_all("div", attrs={"class": "infoblock"})

        len_infoblock = len(list(infoblock))
        name_selector = "#body > div.content > div > span > div:nth-child(2) > h1 > i"
        author_selector = "#body > div.content > div > span > div:nth-child(2) > div.infoblock.authors.visible > div:nth-child(1) > ul"
        journal_selector = "#body > div.content > div > span > div:nth-child(2) > div:nth-child(6) > div.half > span > a"
        year_selector = "#body > div.content > div > span > div:nth-child(2) > div:nth-child(6) > div.half > div.labels > div.label.year > time"
        field_science_selector = "#body > div.content > div > span > div:nth-child(2) > div:nth-child(6) > div.half-right > ul"

        keyword_selector = None if len_infoblock == 16 else "#body > div.content > div > span > div:nth-child(2) > div:nth-child(7)"
        annotation_selector = None if len_infoblock < 18 else "#body > div.content > div > span > div:nth-child(2) > div:nth-child(8) > div > p"
        text_selector = f"#body > div.content > div > span > div:nth-child(2) > div:nth-child({len_infoblock - 2}) > div > div"

        name = self.get_element_web_driver_wait(name_selector).text
        author = self.get_element_web_driver_wait(author_selector).text
        journal = self.get_element_web_driver_wait(journal_selector).text
        year = self.get_element_web_driver_wait(year_selector).text
        field_science = self.get_element_web_driver_wait(field_science_selector).text

        if keyword_selector:
            keyword = self.get_element_web_driver_wait(keyword_selector).text
            if not keyword.find("АННОТАЦИЯ"):
                annotation_selector = "#body > div.content > div > span > div:nth-child(2) > div:nth-child(7) > div > p"
                keyword = ""
            else:
                keyword_selector = "#body > div.content > div > span > div:nth-child(2) > div:nth-child(7) > div > i"
                keyword = self.get_element_web_driver_wait(keyword_selector).text
        else:
            keyword = ""

        if annotation_selector:
            annotation = self.get_element_web_driver_wait(annotation_selector).text
        else:
            annotation = ""

        text = self.get_element_web_driver_wait(text_selector).text

        return name, author, journal, year, field_science, keyword, annotation, text

    def parce_page(self):
        link_element = "#body > div.content > div > div.visible > div > ul"
        link_html = self.get_element_web_driver_wait(link_element).get_attribute('innerHTML')
        soup = BeautifulSoup(link_html, 'html.parser')
        a_link = soup.find_all("a", href=True)

        path = Path("dataset.csv")

        if path.is_file():
            base_dataset = pd.read_csv(path, index_col=0)
        else:
            base_dataset = pd.DataFrame(columns=["Название", "Автор", "Журнал", "Год", "Текст"])

        names, authors, journals, years, field_sciences, keywords, annotations, texts = [], [], [], [], [], [], [], []
        for el in tqdm(a_link):
            name, author, journal, year, field_science, keyword, annotation, text = self.parce_article_page(el["href"])
            names.append(name)
            authors.append(author)
            journals.append(journal)
            years.append(year)
            field_sciences.append(field_science)
            keywords.append(keyword)
            annotations.append(annotation)
            texts.append(text)

        dataset = pd.DataFrame({
            "Название": names,
            "Автор": authors,
            "Журнал": journals,
            "Год": years,
            "Область наук": field_sciences,
            "Ключевые слова": keywords,
            "Аннотация": annotations,
            "Текст": texts,
        })

        pd.concat([base_dataset, dataset]).to_csv(path)

    def run(self, n_pages):
        self.init_driver()

        for i in tqdm(range(n_pages)):
            self.get_page(i)
            self.parce_page()


if __name__ == "__main__":
    CyberLeninka().run(1)
