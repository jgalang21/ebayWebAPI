from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)


#search ebay listings with search string
@app.route('/search/<query>')
def searchEbay(query):
    app.logger.info('Executing search query: ' + query)
    queryResults = query_ebay_listings(query)
    return jsonify(queryResults)



def query_ebay_listings(query):
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_ipg=100&rt=nc&LH_Sold=1"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    

    if response.status_code == 200:
        app.logger.info('Executed query..')

        soup = BeautifulSoup(response.text, 'html.parser')

        #if nothing shows up on ebay's side
        if "No results found" in response.text:
            app.logger.info('No results were found in the query, exiting')
            return {"data" : "No results found!"}


        sold_items = soup.find_all('div', class_='s-item__wrapper clearfix')

        app.logger.info(len(sold_items))

        if not sold_items:
            app.logger.info("No sold items found on the page.")

            return {"data" : "No results found!"}
        
        data = []
        for item in sold_items:

            #error handling where if one of the elements were missing it would fail

            titleElement = item.find('div', class_='s-item__title')
            title = titleElement.text.strip() if titleElement else '<Title not found>'

            if "Shop on eBay" in title: #ignore first element, idk why it's there
                continue

            priceElement = item.find('span', class_='s-item__price') 
            
            bestOffer = 'N'    
           


            item_info = item.find('div', class_='s-item__info')

            # Find the price container within the entire item_info section
            price_container = item_info.find('span', class_='s-item__price')

            # Check if the price container contains a <s> (strikethrough) element
            priceBO = price_container.find('s')




            print(price_container)
         
            if priceBO:
                bestOffer = 'Y'
                

            price = priceElement.text.strip() if priceElement else '<Price not found>'

            date_element = item.find('span', class_='POSITIVE')
            date = date_element.text.strip() if date_element else '<Date not found>'

            href_element = item.find('a', class_='s-item__link')
            href = href_element['href'] if href_element and 'href' in href_element.attrs else '<href not found>'

            

            data.append({
                "title" : title,
                "price" : price,
                "date" : date,
                "url": href,
                "bestOffer" : bestOffer
            })

        return{"data" : data}



    else:
        app.logger.info('Query failed to execute')


    return response.status_code 



if __name__ == '__main__':
    app.run(debug=True)
