import bottlenose
import xmltodict
from config import AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_REGION

amazon = bottlenose.Amazon(
    AWSAccessKeyId=AMAZON_ACCESS_KEY,
    AWSSecretAccessKey=AMAZON_SECRET_KEY,
    AssociateTag=AMAZON_ASSOCIATE_TAG,
    Region=AMAZON_REGION
)

def search_amazon(query):
    response = amazon.ItemSearch(Keywords=query, SearchIndex="All", ResponseGroup="Large")
    data = xmltodict.parse(response)
    
    try:
        item = data['ItemSearchResponse']['Items']['Item'][0]
        title = item['ItemAttributes']['Title']
        asin = item['ASIN']
        detail_page_url = item["DetailPageURL"]
        price = item.get('OfferSummary', {}).get('LowestNewPrice', {}).get('FormattedPrice', 'N/A')
        rating = item.get("CustomerReviews", {}).get("AverageRating", "N/A")
        image = item.get("LargeImage", {}).get("URL", None)

        return {
            "title": title,
            "price": price,
            "rating": rating,
            "asin": asin,
            "url": detail_page_url,
            "image": image
        }
        
    except Exception as e:
        print("Error:", e)
        return None
        
