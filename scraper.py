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
        company_full_name = soup.find('h4', class_="company-inner-title")
        company_full_name = f"*{company_full_name.get_text(strip=True)}*\n"
        tbodies = soup.find_all('tbody')
        
        symbol_details = [company_full_name]
        for tbody in tbodies:
            tr = tbody.find('tr')
            th = tr.find('th') # heading
            td = tr.find('td') # value
    
            if th.text.strip() == "% Dividend":
                break
    
            td_text = td.get_text(strip=True)
            symbol_details.append(f"{th.text.strip()}: `{td_text}`")
        
        return symbol_details
    
    def scrape_company_details(self, query_symbol):
        soup = self.get_company_details(query_symbol)
        
        if soup:
            return self.parse_company_general_details(soup)
