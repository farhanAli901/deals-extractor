import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re

class AmazonDealsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_page(self, url):
        """Fetch a page with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                time.sleep(random.uniform(2, 4))
                return response.text
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    return None
    
    def extract_deal_links(self, deals_page_url):
        """Extract all deal links from the deals page"""
        print(f"Fetching deals page: {deals_page_url}")
        html = self.get_page(deals_page_url)
        
        if not html:
            print("Failed to fetch deals page")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        deal_links = []
        
        # Primary selector
        primary_selector = 'a[data-testid="product-card-link"]'
        
        # Fallback selectors
        fallback_selectors = [
            'a[href*="/dp/"]',
            'a.a-link-normal[href*="/dp/"]',
            'div[data-deal-id] a[href*="/dp/"]',
        ]
        
        links = soup.select(primary_selector)
        
        if not links:
            print("Primary selector found no links, trying fallbacks...")
            for selector in fallback_selectors:
                links = soup.select(selector)
                if links:
                    print(f"Found links using fallback selector: {selector}")
                    break
        
        for link in links:
            href = link.get('href')
            if href:
                if href.startswith('/'):
                    href = f"https://www.amazon.ae{href}"
                elif not href.startswith('http'):
                    continue
                
                if '/dp/' in href:
                    clean_url = href.split('?')[0]
                    deal_links.append(clean_url)
        
        deal_links = list(dict.fromkeys(deal_links))
        print(f"Found {len(deal_links)} unique deals")
        return deal_links
    
    def extract_price_numeric(self, price_str):
        """Extract numeric value from price string"""
        if not price_str or price_str == "Not found":
            return None
        try:
            # Remove currency, commas, spaces
            numeric = re.sub(r'[^\d.]', '', price_str)
            return float(numeric)
        except:
            return None
    
    def extract_deal_details(self, product_url):
        """Extract details from a single product/deal page"""
        print(f"\n{'='*60}")
        print(f"Scraping: {product_url}")
        print(f"{'='*60}")
        
        html = self.get_page(product_url)
        
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        deal_data = {
            "url": product_url,
            "title": "Not found",
            "brand": "Not found",
            "category": "Not found",
            "original_price": "Not found",
            "discounted_price": "Not found",
            "discount_percentage": "Not found",
            "expiry_date": "Not found",
            "description": "Not found",
            "product_image": "Not found"
        }
        
        # Extract Title
        title = soup.select_one('#productTitle')
        if title:
            deal_data["title"] = title.get_text(strip=True)
            print(f"✓ Title: {deal_data['title'][:60]}...")
        
        # Extract Brand
        brand = soup.select_one('#bylineInfo')
        if brand:
            brand_text = brand.get_text(strip=True)
            brand_text = brand_text.replace('Visit the', '').replace('Brand:', '').replace('Store', '').strip()
            deal_data["brand"] = brand_text
            print(f"✓ Brand: {deal_data['brand']}")
        
        # Extract Category
        breadcrumb = soup.select('#wayfinding-breadcrumbs_container ul li a')
        if not breadcrumb:
            breadcrumb = soup.select('#wayfinding-breadcrumbs_feature_div ul li a')
        if not breadcrumb:
            breadcrumb = soup.select('div[id*="breadcrumb"] a')
        
        if breadcrumb:
            categories = [cat.get_text(strip=True) for cat in breadcrumb if cat.get_text(strip=True)]
            if categories:
                deal_data["category"] = ' > '.join(categories)
                print(f"✓ Category: {deal_data['category']}")
        
        # Extract Original Price
        original_price_elem = soup.select_one('span.a-price[data-a-strike="true"] .a-offscreen')
        if original_price_elem:
            deal_data["original_price"] = original_price_elem.get_text(strip=True)
            print(f"✓ Original Price: {deal_data['original_price']}")
        
        # Extract Discount Percentage
        discount = soup.select_one('span.savingsPercentage')
        if discount:
            deal_data["discount_percentage"] = discount.get_text(strip=True)
            print(f"✓ Discount: {deal_data['discount_percentage']}")
        
        # Extract Discounted Price - MULTIPLE METHODS
        print(f"\n--- Extracting Discounted Price ---")
        
        # Method 1: .aok-offscreen with "savings" text
        print(f"Method 1: Checking .aok-offscreen elements...")
        aok_offscreens = soup.select('.aok-offscreen')
        print(f"  Found {len(aok_offscreens)} .aok-offscreen elements")
        
        for i, elem in enumerate(aok_offscreens):
            text = elem.get_text(strip=True)
            if text and 'AED' in text and 'with' in text.lower() and 'savings' in text.lower():
                price_part = text.split('with')[0].strip()
                deal_data["discounted_price"] = price_part.replace('\xa0', ' ')
                print(f"  ✓ FOUND via .aok-offscreen: {deal_data['discounted_price']}")
                break
        
        # Method 2: Build from .a-price-whole and .a-price-fraction
        if deal_data["discounted_price"] == "Not found":
            print(f"Method 2: Building from price parts...")
            price_symbol = soup.select_one('.a-price:not([data-a-strike]) .a-price-symbol')
            price_whole = soup.select_one('.a-price:not([data-a-strike]) .a-price-whole')
            price_fraction = soup.select_one('.a-price:not([data-a-strike]) .a-price-fraction')
            
            if price_whole:
                symbol = price_symbol.get_text(strip=True) if price_symbol else "AED"
                whole = price_whole.get_text(strip=True).replace(',', '').strip()
                fraction = price_fraction.get_text(strip=True) if price_fraction else "00"
                
                deal_data["discounted_price"] = f"{symbol} {whole}.{fraction}"
                print(f"  ✓ BUILT from parts: {deal_data['discounted_price']}")
        
        # Method 3: Try .a-offscreen from non-strike prices
        if deal_data["discounted_price"] == "Not found":
            print(f"Method 3: Checking .a-offscreen in non-strike prices...")
            offscreen_prices = soup.select('.a-price:not([data-a-strike="true"]) .a-offscreen')
            for elem in offscreen_prices:
                text = elem.get_text(strip=True)
                if text and 'AED' in text and len(text) > 3:
                    deal_data["discounted_price"] = text
                    print(f"  ✓ FOUND in .a-offscreen: {deal_data['discounted_price']}")
                    break
        
        # Method 4: CALCULATE from original price and discount
        if deal_data["discounted_price"] == "Not found":
            print(f"Method 4: Attempting calculation...")
            print(f"  Original: {deal_data['original_price']}")
            print(f"  Discount: {deal_data['discount_percentage']}")
            
            if deal_data["original_price"] != "Not found" and deal_data["discount_percentage"] != "Not found":
                try:
                    original_val = self.extract_price_numeric(deal_data["original_price"])
                    discount_match = re.search(r'(\d+)', deal_data["discount_percentage"])
                    
                    if original_val and discount_match:
                        discount_val = float(discount_match.group(1))
                        discounted_val = original_val * (1 - discount_val / 100)
                        deal_data["discounted_price"] = f"AED {discounted_val:.2f}"
                        print(f"  ✓ CALCULATED: {deal_data['discounted_price']}")
                    else:
                        print(f"  ✗ Could not extract numeric values")
                except Exception as e:
                    print(f"  ✗ Calculation failed: {e}")
            else:
                print(f"  ✗ Missing data for calculation")
        
        print(f"--- Final Discounted Price: {deal_data['discounted_price']} ---\n")
        
        # Extract Expiry Date
        expiry_selectors = [
            'span#deal-end-time',
            'span[id*="timer"]',
            'div[data-dealcountdownstring]',
            'span[data-a-expiration-time]',
            '#dealExpiry'
        ]
        for selector in expiry_selectors:
            expiry = soup.select_one(selector)
            if expiry:
                deal_data["expiry_date"] = expiry.get_text(strip=True)
                break
        
        # Extract Description with fallback selectors
        desc_selectors = [
            '#feature-bullets ul li',  # Primary selector
            'div.a-expander-content.a-expander-partial-collapse-content ul li',  # Fallback for "About this item"
            'div[class*="a-expander-content"] ul li'  # Additional fallback
        ]
        
        for selector in desc_selectors:
            desc_elements = soup.select(selector)
            if desc_elements:
                descriptions = []
                for desc in desc_elements[:5]:
                    text = desc.get_text(strip=True)
                    if text and len(text) > 5:
                        descriptions.append(text)
                if descriptions:
                    deal_data["description"] = ' | '.join(descriptions)
                    break  # Stop checking once found
        
        # Extract Product Image
        img = soup.select_one('#imgTagWrapperId img')
        if img:
            img_url = (img.get('src') or 
                      img.get('data-old-hires') or 
                      img.get('data-a-dynamic-image'))
            
            if img_url and img_url.startswith('{'):
                try:
                    import json as json_lib
                    img_dict = json_lib.loads(img_url)
                    img_url = list(img_dict.keys())[0] if img_dict else None
                except:
                    pass
            
            if img_url:
                deal_data["product_image"] = img_url
        
        return deal_data
    
    def scrape_deals(self, deals_page_url, max_deals=None):
        """Main method to scrape all deals"""
        deal_links = self.extract_deal_links(deals_page_url)
        
        if not deal_links:
            print("No deals found on the page")
            return []
        
        if max_deals:
            deal_links = deal_links[:max_deals]
        
        all_deals = []
        for i, link in enumerate(deal_links, 1):
            print(f"\n{'='*60}")
            print(f"Processing deal {i}/{len(deal_links)}")
            print(f"{'='*60}")
            
            deal_data = self.extract_deal_details(link)
            if deal_data:
                all_deals.append(deal_data)
                print(f"\n✓ Successfully scraped deal {i}")
            else:
                print(f"\n✗ Failed to scrape: {link}")
        
        return all_deals
    
    def save_to_json(self, data, filename='amazon_deals.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Data saved to {filename}")
    
    def print_summary(self, deals):
        """Print a summary of scraped deals"""
        print(f"\n{'='*60}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total deals scraped: {len(deals)}")
        
        if deals:
            print(f"\n{'='*60}")
            print("ALL SCRAPED DEALS")
            print(f"{'='*60}\n")
            
            for i, deal in enumerate(deals, 1):
                print(f"\n--- Deal #{i} ---")
                for key, value in deal.items():
                    if key != 'url':
                        print(f"{key.replace('_', ' ').title()}: {value}")


if __name__ == "__main__":
    scraper = AmazonDealsScraper()
    
    deals_url = input("Enter Amazon deals page URL: ").strip()
    limit = input("Enter max number of deals to scrape (press Enter for all): ").strip()
    max_deals = int(limit) if limit.isdigit() else None
    
    print(f"\nStarting scraper...\n")
    deals_data = scraper.scrape_deals(deals_url, max_deals=max_deals)
    
    if deals_data:
        scraper.save_to_json(deals_data)
        scraper.print_summary(deals_data)
    else:
        print("\n✗ No deals were scraped")