import requests
from bs4 import BeautifulSoup

class CompanyDetailsScraper:
    def __init__(self):
        self.base_url = "https://merolagani.com/CompanyDetail.aspx?symbol="
        

    def get_company_details(self, symbol):
        url = self.base_url + symbol
    
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
