import requests
from bs4 import BeautifulSoup

class MeroLaganiScraper:
    def __init__(self):
        self.base_search_url = "https://merolagani.com/CompanyDetail.aspx?symbol="
        self.base_news_url = "https://merolagani.com/Ipo.aspx?type=upcoming"


    def get_latest_ipo_news(self):
        url = self.base_news_url

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        except requests.exceptions.RequestException as e:
            print("Error occurred during the request:", e)
            return None


    def parse_latest_ipo_news(self, soup):
        all_news = soup.find_all('div', class_="media-body")


        news_details = {}
        for idx, news in enumerate(all_news, 0):
            new_news_detail = {}
            new_news_detail['title'] = news.text.strip()
            new_news_detail['link'] = "https://merolagani.com/" + news.find('a', href=True)['href']
            news_details[f"news{idx}"] = new_news_detail

        return news_details


    def get_company_details(self, symbol):
        url = self.base_search_url + symbol
    
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        except requests.exceptions.RequestException as e:
            print("Error occurred during the request:", e)
            return None
    

    def parse_company_general_details(self, soup):
        company_full_name = soup.find('h4', class_="company-inner-title").get_text(strip=True)
        # company_full_name = company_full_name.get_text(strip=True)
        tbodies = soup.find_all('tbody')
        
        symbol_details = {'result': True, 'company_full_name': company_full_name}
        emptyCount = 0
        for tbody in tbodies:
            tr = tbody.find('tr')
            th = tr.find('th') # heading
            td = tr.find('td') # value
    
            if th.text.strip() == "% Dividend":
                break
            
            td_text = td.get_text(strip=True)
            
            if td_text:
                emptyCount += 1

            symbol_details[th.text.strip().lower().replace(' ', '_')] = td_text
            # symbol_details.append(f"{th.text.strip()}: `{td_text}`")
        
        if emptyCount == 0:
            symbol_details['result'] = False

        return symbol_details
    

    def scrape_company_details(self, query_symbol):
        soup = self.get_company_details(query_symbol)
        
        if soup:
            return self.parse_company_general_details(soup)
        

    def scrape_lastest_ipo_news(self):
        soup = self.get_latest_ipo_news()

        if soup:
            return self.parse_latest_ipo_news(soup)