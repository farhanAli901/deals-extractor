from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import threading
import time
from urllib.parse import urlparse
from amazon_scraper import AmazonDealsScraper
from noon_scraper import NoonProductScraper

app = Flask(__name__, static_folder='.')
CORS(app)

# Global variables to track scraping status for each platform
amazon_scraping_status = {
    'is_scraping': False,
    'progress': 0,
    'total': 0,
    'deals_scraped': 0,
    'deals_requested': 0,
    'message': 'Ready'
}

noon_scraping_status = {
    'is_scraping': False,
    'progress': 0,
    'total': 0,
    'deals_scraped': 0,
    'deals_requested': 0,
    'message': 'Ready'
}

def detect_platform(url):
    """Detect if URL is from Amazon or Noon"""
    try:
        domain = urlparse(url).netloc.lower()
        if 'amazon' in domain:
            return 'amazon'
        elif 'noon' in domain:
            return 'noon'
        return None
    except:
        return None

def is_valid_amazon_deal(deal):
    """Check if Amazon deal has both original and discounted prices (not 'Not found')"""
    return (deal.get('original_price', 'Not found') != 'Not found' and 
            deal.get('discounted_price', 'Not found') != 'Not found' and
            'AED' in deal.get('discounted_price', ''))

def is_valid_noon_deal(deal):
    """Check if Noon deal has both original and discounted prices"""
    return (deal.get('original_price') and deal.get('original_price') != 'Not found' and
            deal.get('discounted_price') and deal.get('discounted_price') != 'Not found' and
            deal.get('original_price') != deal.get('discounted_price'))

def scrape_amazon_deals_background(url, max_deals=None):
    """Background function to scrape Amazon deals"""
    global amazon_scraping_status
    
    try:
        amazon_scraping_status = {
            'is_scraping': True,
            'progress': 0,
            'total': 0,
            'deals_scraped': 0,
            'deals_requested': max_deals if max_deals else 0,
            'message': 'Starting Amazon scraper...'
        }
        
        scraper = AmazonDealsScraper()
        
        # Extract deal links first
        amazon_scraping_status['message'] = 'Finding deals...'
        deal_links = scraper.extract_deal_links(url)
        
        if not deal_links:
            amazon_scraping_status = {
                'is_scraping': False,
                'progress': 0,
                'total': 0,
                'deals_scraped': 0,
                'deals_requested': max_deals if max_deals else 0,
                'message': 'No deals found on the page'
            }
            return
        
        if max_deals:
            deal_links = deal_links[:max_deals]
        
        amazon_scraping_status['total'] = len(deal_links)
        amazon_scraping_status['deals_requested'] = max_deals if max_deals else len(deal_links)
        all_deals = []
        
        # Scrape each deal
        for i, link in enumerate(deal_links, 1):
            amazon_scraping_status['progress'] = i
            amazon_scraping_status['message'] = f'Scraping product {i} of {len(deal_links)}...'
            
            deal_data = scraper.extract_deal_details(link)
            if deal_data and is_valid_amazon_deal(deal_data):
                all_deals.append(deal_data)
                amazon_scraping_status['deals_scraped'] = len(all_deals)
        
        # Filter only valid deals before saving
        valid_deals = [deal for deal in all_deals if is_valid_amazon_deal(deal)]
        
        # Save to JSON
        scraper.save_to_json(valid_deals, 'amazon_deals.json')
        
        amazon_scraping_status = {
            'is_scraping': False,
            'progress': len(deal_links),
            'total': len(deal_links),
            'deals_scraped': len(valid_deals),
            'deals_requested': max_deals if max_deals else len(deal_links),
            'message': f'Successfully scraped {len(valid_deals)} valid deals out of {max_deals if max_deals else len(deal_links)} requested'
        }
        
    except Exception as e:
        amazon_scraping_status = {
            'is_scraping': False,
            'progress': 0,
            'total': 0,
            'deals_scraped': 0,
            'deals_requested': max_deals if max_deals else 0,
            'message': f'Error: {str(e)}'
        }

def scrape_noon_deals_background(url, max_deals=None):
    """Background function to scrape Noon deals"""
    global noon_scraping_status
    
    try:
        print(f"\n{'='*60}")
        print(f"[INFO] Starting Noon scraper")
        print(f"[INFO] URL: {url}")
        print(f"[INFO] Max deals requested: {max_deals}")
        print(f"{'='*60}\n")
        
        noon_scraping_status = {
            'is_scraping': True,
            'progress': 0,
            'total': 0,
            'deals_scraped': 0,
            'deals_requested': max_deals if max_deals else 0,
            'message': 'Starting Noon scraper...'
        }
        
        scraper = NoonProductScraper()
        
        # Get product list from page
        noon_scraping_status['message'] = 'Finding deals...'
        print(f"[INFO] Fetching product list from Noon...")
        product_cards = scraper.scrape_products_from_list(url, only_deals=True)
        print(f"[INFO] Found {len(product_cards) if product_cards else 0} products on page")
        
        if not product_cards:
            noon_scraping_status = {
                'is_scraping': False,
                'progress': 0,
                'total': 0,
                'deals_scraped': 0,
                'deals_requested': max_deals if max_deals else 0,
                'message': 'No deals found on the page'
            }
            return
        
        if max_deals:
            product_cards = product_cards[:max_deals]
        
        noon_scraping_status['total'] = len(product_cards)
        noon_scraping_status['deals_requested'] = max_deals if max_deals else len(product_cards)
        all_deals = []
        
        # Scrape details for each product
        for i, product_card in enumerate(product_cards, 1):
            noon_scraping_status['progress'] = i
            noon_scraping_status['message'] = f'Scraping product {i} of {len(product_cards)}...'
            
            # Add small delay to avoid overwhelming the server
            if i > 1:
                time.sleep(1)  # 1 second delay between products
            
            try:
                product_detail = scraper.scrape_product_detail(product_card.url)
                
                # Format prices to include AED currency if not present
                original_price = product_detail.original_price or product_card.original_price or 'Not found'
                discounted_price = product_detail.offered_price or product_card.offered_price or 'Not found'
                
                # Add AED prefix if it's just a number
                if original_price != 'Not found' and not original_price.startswith('AED'):
                    original_price = f"AED {original_price}"
                if discounted_price != 'Not found' and not discounted_price.startswith('AED'):
                    discounted_price = f"AED {discounted_price}"
                
                # Create deal object in similar format to Amazon
                deal_data = {
                    'url': product_card.url,
                    'title': product_detail.title or product_card.title or 'Not found',
                    'brand': 'Not found',  # Noon doesn't always have brand easily accessible
                    'category': 'Not found',
                    'original_price': original_price,
                    'discounted_price': discounted_price,
                    'discount_percentage': product_detail.profit or 'Not found',
                    'expiry_date': 'Not found',
                    'description': product_detail.description or 'Not found',
                    'product_image': product_detail.image or product_card.image or 'Not found'
                }
                
                print(f"[DEBUG Noon] Product {i}: {deal_data.get('title', 'N/A')[:50]}")
                print(f"[DEBUG Noon] Original: {deal_data.get('original_price')}, Discounted: {deal_data.get('discounted_price')}")
                print(f"[DEBUG Noon] Is valid: {is_valid_noon_deal(deal_data)}")
                
                if is_valid_noon_deal(deal_data):
                    all_deals.append(deal_data)
                    noon_scraping_status['deals_scraped'] = len(all_deals)
                else:
                    print(f"[DEBUG Noon] Product skipped - validation failed")
            except Exception as e:
                print(f"[ERROR Noon] Error scraping product {i}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # Filter only valid deals before saving
        valid_deals = [deal for deal in all_deals if is_valid_noon_deal(deal)]
        
        # Save to JSON
        with open('noon_deals.json', 'w', encoding='utf-8') as f:
            json.dump(valid_deals, f, indent=2, ensure_ascii=False)
        
        noon_scraping_status = {
            'is_scraping': False,
            'progress': len(product_cards),
            'total': len(product_cards),
            'deals_scraped': len(valid_deals),
            'deals_requested': max_deals if max_deals else len(product_cards),
            'message': f'Successfully scraped {len(valid_deals)} valid deals out of {max_deals if max_deals else len(product_cards)} requested'
        }
        
    except Exception as e:
        print(f"\n[ERROR] Noon scraping failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        noon_scraping_status = {
            'is_scraping': False,
            'progress': 0,
            'total': 0,
            'deals_scraped': 0,
            'deals_requested': max_deals if max_deals else 0,
            'message': f'Error: {str(e)}'
        }

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    """Start scraping process - detects platform automatically"""
    global amazon_scraping_status, noon_scraping_status
    
    data = request.json
    url = data.get('url', '')
    max_deals = data.get('max_deals', None)
    
    if not url:
        return jsonify({
            'success': False,
            'message': 'URL is required'
        }), 400
    
    # Detect platform
    platform = detect_platform(url)
    
    if platform == 'amazon':
        if amazon_scraping_status['is_scraping']:
            return jsonify({
                'success': False,
                'message': 'Amazon scraping is already in progress'
            }), 400
        
        # Start Amazon scraping in background thread
        thread = threading.Thread(target=scrape_amazon_deals_background, args=(url, max_deals))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Amazon scraping started',
            'platform': 'amazon'
        })
    
    elif platform == 'noon':
        if noon_scraping_status['is_scraping']:
            return jsonify({
                'success': False,
                'message': 'Noon scraping is already in progress'
            }), 400
        
        # Start Noon scraping in background thread
        thread = threading.Thread(target=scrape_noon_deals_background, args=(url, max_deals))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Noon scraping started',
            'platform': 'noon'
        })
    
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid URL. Please enter an Amazon or Noon URL'
        }), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current scraping status for a platform"""
    platform = request.args.get('platform', 'amazon')
    
    if platform == 'noon':
        return jsonify(noon_scraping_status)
    else:
        return jsonify(amazon_scraping_status)

@app.route('/api/deals', methods=['GET'])
def get_deals():
    """Get current deals from JSON file for a platform"""
    platform = request.args.get('platform', 'amazon')
    
    try:
        filename = 'noon_deals.json' if platform == 'noon' else 'amazon_deals.json'
        
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                deals = json.load(f)
                # Filter to only include valid deals
                if platform == 'noon':
                    valid_deals = [deal for deal in deals if is_valid_noon_deal(deal)]
                else:
                    valid_deals = [deal for deal in deals if is_valid_amazon_deal(deal)]
                return jsonify({
                    'success': True,
                    'deals': valid_deals,
                    'count': len(valid_deals),
                    'platform': platform
                })
        else:
            return jsonify({
                'success': True,
                'deals': [],
                'count': 0,
                'platform': platform
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'deals': [],
            'count': 0,
            'platform': platform
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Amazon Deals Scraper Server Starting...")
    print("=" * 60)
    print("📍 Server running at: http://localhost:5000")
    print("🌐 Open your browser and visit: http://localhost:5000")
    print("💡 Note: Noon scraper temporarily disabled")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

