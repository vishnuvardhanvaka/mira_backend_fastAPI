from selectorlib import Extractor
import requests
import json
from time import sleep

'''
product_image_urls:
    css: 'img.s-image'
    xpath: null
    type: Attribute
    attribute: src
'''

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('search_results.yml')

def scrape(url):
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create
    return e.extract(r.text)

def start_scrape(searchable_que):
    product_data = []
    weight_rating=0.7
    weight_review=0.3
    amazon_search_query = searchable_que.replace(" ", "+")
    urls=[f'https://www.amazon.in/s?k={amazon_search_query}']
    for url in urls:
        data = scrape(url)
        if data['products']!=None:
            print(data)
            product_data=data['products']

    print(len(product_data))
    for product in product_data:
        if product['rating']==None:
            product['rating']=str(0)
            product['reviews']=str(0)
        product['rating']=float(product['rating'].split(' ')[0])
        product['reviews']=float(''.join(product['reviews'].split(',')))
        product['url']='https://www.amazon.in'+product['url']
        # product['score']=round((product['rating']*weight_rating)+(product['reviews']*weight_review),2)

    #product_data=sorted(product_data,key=lambda x:x['rating'],reverse=True)[:3]

    for product in product_data:
        for key in product:
            print(f'{key} : {product[key]}')
        print('------------------')
    print(type(product_data))
    return product_data[:5]
