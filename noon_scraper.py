import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import json
import time


@dataclass
class Size:
    """Data class to store product size option information"""
    label: str                          # Size label (S, M, L, XL, XXL, etc.)
    link: Optional[str] = None          # URL link to this size variant
    is_active: bool = False             # Whether this size is currently selected
    is_disabled: bool = False           # Whether this size option is disabled
    is_out_of_stock: bool = False       # Whether this size is out of stock

    def to_dict(self) -> Dict:
        """Convert size data to dictionary"""
        return asdict(self)


@dataclass
class ProductCard:
    """Data class for minimal product information from product list/category pages"""
    url: str                           # Product detail page URL
    title: Optional[str] = None        # Product title/name
    image: Optional[str] = None        # Product image URL
    offered_price: Optional[str] = None # Current selling price
    original_price: Optional[str] = None # Original price (if on discount)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def __hash__(self) -> int:
        """Make dataclass hashable for deduplication"""
        return hash(self.url)
    
    def __eq__(self, other) -> bool:
        """Compare by URL for deduplication"""
        if not isinstance(other, ProductCard):
            return False
        return self.url == other.url


@dataclass
class ProductDetail:
    """Data class to store product information from noon.com detail pages"""
    image: Optional[str] = None
    title: Optional[str] = None
    offered_price: Optional[str] = None
    original_price: Optional[str] = None
    profit: Optional[str] = None
    description: Optional[str] = None
    thumbnails: List[str] = None
    sizes: List[Size] = None

    def __post_init__(self):
        """Initialize thumbnails and sizes as empty lists if None"""
        if self.thumbnails is None:
            self.thumbnails = []
        if self.sizes is None:
            self.sizes = []

    def to_dict(self) -> Dict:
        """Convert product data to dictionary"""
        return asdict(self)


class NoonProductScraper:
    """Scraper for extracting product information from noon.com"""
    
    # Selectors for product detail pages
    SELECTORS = {
        "image": ".GalleryV2-module-scss-module__hlK6zG__magnifyWrapper img",
        "thumbnails": ".GalleryV2-module-scss-module__hlK6zG__thumbnailElement img",
        "title": ".ProductTitle-module-scss-module__EXiEUa__title",
        "offered_price": ".PriceOfferV2-module-scss-module__dHtRPW__priceNowText",
        "original_price": ".PriceOfferV2-module-scss-module__dHtRPW__priceWasText",
        "profit": ".PriceOfferV2-module-scss-module__dHtRPW__profit",
        "description": ".SectionWrapper-module-scss-module__3lhB-a__sectionBody",
        "sizes": ".ButtonOptions-module-scss-module__Pu6iuq__buttonOptionsCtr .ButtonOptions-module-scss-module__Pu6iuq__optionButton",
    }
    
    # Selectors for product list pages
    LIST_SELECTORS = {
        "product_card": ".PBoxLinkHandler-module-scss-module__WvRpgq__linkWrapper",
        "product_link": ".PBoxLinkHandler-module-scss-module__WvRpgq__productBoxLink",
        "product_title": ".ProductDetailsSection-module-scss-module__Y6u1Qq__title",
        "product_image": ".ProductImageCarousel-module-scss-module__SlkSTG__productImage",
        "offered_price": ".Price-module-scss-module__q-4KEG__amount",
        "original_price": ".Price-module-scss-module__q-4KEG__oldPrice",
    }
    
    TIMEOUT = 30  # Request timeout in seconds (increased from 10)
    
    def __init__(self, timeout: int = TIMEOUT):
        """
        Initialize the scraper with optional timeout configuration
        
        Args:
            timeout (int): Request timeout in seconds (default: 30)
        """
        self.timeout = timeout
        self.missing_selectors: List[str] = []
        # Create a persistent session for better performance
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch the webpage and parse it with retry logic
        
        Args:
            url (str): The URL to scrape
            retries (int): Number of retry attempts (default: 3)
            
        Returns:
            BeautifulSoup: Parsed HTML content
            
        Raises:
            ValueError: If URL is invalid or page fails to load after retries
        """
        # Validate URL format
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
        except Exception as e:
            raise ValueError(f"URL validation failed: {e}")
        
        # Attempt to fetch the webpage with retries
        last_error = None
        for attempt in range(retries):
            try:
                # Add a small delay between retries to avoid rate limiting
                if attempt > 0:
                    time.sleep(2 * attempt)  # Progressive delay: 2s, 4s
                    
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.exceptions.Timeout as e:
                last_error = f"Request timeout: Page took longer than {self.timeout} seconds to load"
                print(f"[WARNING] Attempt {attempt + 1}/{retries} failed: Timeout")
                if attempt < retries - 1:
                    continue
            except requests.exceptions.ConnectionError as e:
                last_error = "Connection error: Failed to connect to the website. Check your internet connection."
                print(f"[WARNING] Attempt {attempt + 1}/{retries} failed: Connection error")
                if attempt < retries - 1:
                    continue
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                last_error = f"HTTP Error {status_code}: The webpage returned an error."
                print(f"[WARNING] Attempt {attempt + 1}/{retries} failed: HTTP {status_code}")
                if attempt < retries - 1:
                    continue
            except Exception as e:
                last_error = f"Failed to fetch webpage: {str(e)}"
                print(f"[WARNING] Attempt {attempt + 1}/{retries} failed: {str(e)}")
                if attempt < retries - 1:
                    continue
        
        # All retries failed
        raise ValueError(last_error if last_error else "Failed to fetch webpage after multiple attempts")
    
    def _extract_attribute(self, soup: BeautifulSoup, selector: str, attribute: str = "text") -> Optional[str]:
        """
        Extract data from a specific selector
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            selector (str): CSS selector
            attribute (str): Attribute to extract ('text' for element text, or specific HTML attribute)
            
        Returns:
            str: Extracted data or None if not found
        """
        try:
            element = soup.select_one(selector)
            if element:
                if attribute == "text":
                    return element.get_text(strip=True)
                else:
                    return element.get(attribute)
            return None
        except Exception:
            return None
    
    def _extract_thumbnails(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """
        Extract multiple thumbnail URLs from selector
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            selector (str): CSS selector for thumbnail images
            
        Returns:
            List[str]: List of thumbnail URLs
        """
        try:
            elements = soup.select(selector)
            thumbnails = []
            for element in elements:
                src = element.get("src")
                if src:
                    thumbnails.append(src)
            return thumbnails
        except Exception:
            return []
    
    def _extract_sizes(self, soup: BeautifulSoup, selector: str) -> List[Size]:
        """
        Extract size options from selector
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            selector (str): CSS selector for size option buttons
            
        Returns:
            List[Size]: List of Size objects with availability information
        """
        try:
            elements = soup.select(selector)
            sizes = []
            
            for element in elements:
                # Extract size label from text content
                label = element.get_text(strip=True)
                
                # Extract link
                link = element.get("href")
                
                # Check classes for state information
                classes = element.get("class", [])
                is_active = "ButtonOptions-module-scss-module__Pu6iuq__active" in classes
                is_disabled = "ButtonOptions-module-scss-module__Pu6iuq__disabled" in classes
                is_out_of_stock = "ButtonOptions-module-scss-module__Pu6iuq__oos" in classes
                
                # Create Size object
                size = Size(
                    label=label,
                    link=link,
                    is_active=is_active,
                    is_disabled=is_disabled,
                    is_out_of_stock=is_out_of_stock
                )
                sizes.append(size)
            
            return sizes
        except Exception:
            return []
    
    def _validate_selectors(self, soup: BeautifulSoup) -> None:
        """
        Check if all required selectors are found on the page
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
        """
        self.missing_selectors = []
        
        for selector_name, selector in self.SELECTORS.items():
            # For thumbnails and sizes, check if any elements exist
            if selector_name in ["thumbnails", "sizes"]:
                if not soup.select(selector):
                    self.missing_selectors.append(selector_name)
            else:
                if not soup.select_one(selector):
                    self.missing_selectors.append(selector_name)
    
    def scrape_product_detail(self, url: str) -> ProductDetail:
        """
        Scrape product information from a noon.com product detail page.
        
        Args:
            url (str): The noon.com product detail page URL to scrape
            
        Returns:
            ProductDetail: Object containing extracted product data
            
        Raises:
            ValueError: If page fails to load or critical selectors are missing
        """
        # Reset missing selectors for fresh attempt
        self.missing_selectors = []
        
        # Fetch the webpage
        soup = self.fetch_page(url)
        if not soup:
            raise ValueError("Failed to parse the webpage content")
        
        # Validate selectors
        self._validate_selectors(soup)
        
        # Report missing selectors
        if self.missing_selectors:
            missing_list = ", ".join(self.missing_selectors)
            warning_msg = (
                f"\n⚠️  WARNING: Missing selectors detected: {missing_list}\n"
                f"   This could indicate:\n"
                f"   1. The URL does not belong to a noon.com product details page\n"
                f"   2. The page structure has changed and the scraper needs to be updated\n"
                f"   3. The product page is currently unavailable\n"
            )
            print(warning_msg)
        
        # Extract data using selectors
        product = ProductDetail(
            image=self._extract_attribute(soup, self.SELECTORS["image"], "src"),
            title=self._extract_attribute(soup, self.SELECTORS["title"]),
            offered_price=self._extract_attribute(soup, self.SELECTORS["offered_price"]),
            original_price=self._extract_attribute(soup, self.SELECTORS["original_price"]),
            profit=self._extract_attribute(soup, self.SELECTORS["profit"]),
            description=self._extract_attribute(soup, self.SELECTORS["description"]),
            thumbnails=self._extract_thumbnails(soup, self.SELECTORS["thumbnails"]),
            sizes=self._extract_sizes(soup, self.SELECTORS["sizes"]),
        )
        
        return product
    
    def scrape_products_from_list(self, url: str, only_deals: bool = True, save_to_file: Optional[str] = None) -> List[ProductCard]:
        """
        Scrape product URLs and basic info from a category/landing/deals page.
        
        Args:
            url (str): The category/landing page URL to scrape
            only_deals (bool): If True, only include products with original_price (discounted). 
                             Default: True (only deals/discounted products)
            save_to_file (str, optional): If provided, save results to JSON file. Default: None (no file)
            
        Returns:
            List[ProductCard]: List of unique products (no duplicates)
            
        Raises:
            ValueError: If page fails to load
        """
        # Fetch the webpage
        soup = self.fetch_page(url)
        if not soup:
            raise ValueError("Failed to parse the webpage content")
        
        products_set: Set[ProductCard] = set()
        
        # Find all product cards
        product_cards = soup.select(self.LIST_SELECTORS["product_card"])
        
        if not product_cards:
            print(f"[WARNING] No product cards found on the page. "
                  f"This could indicate the selectors need updating or the page structure changed.")
            return []
        
        for card in product_cards:
            try:
                # Extract product URL
                link_element = card.select_one(self.LIST_SELECTORS["product_link"])
                if not link_element or not link_element.get("href"):
                    continue
                
                product_url = link_element.get("href")
                # Handle relative URLs
                if product_url.startswith("/"):
                    product_url = "https://www.noon.com" + product_url
                
                # Extract title
                title = self._extract_attribute(card, self.LIST_SELECTORS["product_title"])
                
                # Extract image (first product image in carousel)
                image = self._extract_attribute(card, self.LIST_SELECTORS["product_image"], "src")
                
                # Extract prices
                offered_price = self._extract_attribute(card, self.LIST_SELECTORS["offered_price"])
                original_price = self._extract_attribute(card, self.LIST_SELECTORS["original_price"])
                
                # Filter by deals if only_deals is True
                if only_deals and not original_price:
                    continue
                
                # Create ProductCard object
                product_card = ProductCard(
                    url=product_url,
                    title=title,
                    image=image,
                    offered_price=offered_price,
                    original_price=original_price
                )
                
                # Add to set (duplicates automatically removed)
                products_set.add(product_card)
                
            except Exception as e:
                # Skip products with extraction errors
                continue
        
        # Convert set back to list
        products_list = list(products_set)
        
        # Save to file if requested
        if save_to_file:
            try:
                with open(save_to_file, 'w', encoding='utf-8') as f:
                    json.dump(
                        [p.to_dict() for p in products_list],
                        f,
                        indent=2,
                        ensure_ascii=False
                    )
                print(f"[OK] Saved {len(products_list)} products to {save_to_file}")
            except Exception as e:
                print(f"[ERROR] Failed to save to file: {e}")
        
        return products_list


# Example usage
if __name__ == "__main__":
    # Initialize the scraper
    scraper = NoonProductScraper()
    
    print("=" * 80)
    print("Noon.com Deals Scraper")
    print("=" * 80)
    
    # Get deals URL from user
    deals_url = input("\nEnter the deals/category URL: ").strip()
    
    if not deals_url:
        print("[ERROR] URL cannot be empty")
        exit(1)
    
    try:
        print("\n[*] Fetching products from the page...")
        # Scrape products from the deals page
        products = scraper.scrape_products_from_list(
            deals_url,
            only_deals=True,
            save_to_file=None
        )
        
        if not products:
            print("[WARNING] No products found on the page.")
            exit(1)
        
        print(f"[OK] Found {len(products)} products. Checking for deals (profit info)...\n")
        
        # Scrape details for each product to get profit information
        deals_with_profit = []
        
        for i, product_card in enumerate(products, 1):
            try:
                print(f"[{i}/{len(products)}] Scraping: {product_card.title}...", end=" ")
                product_detail = scraper.scrape_product_detail(product_card.url)
                
                # Check if product has profit (meaning it's on deal)
                if product_detail.profit:
                    deals_with_profit.append({
                        'title': product_detail.title or product_card.title,
                        'offered_price': product_detail.offered_price or product_card.offered_price,
                        'original_price': product_detail.original_price or product_card.original_price,
                        'profit': product_detail.profit,
                        'description': product_detail.description,
                        'image': product_detail.image or product_card.image,
                        'thumbnails': product_detail.thumbnails,
                        'url': product_card.url
                    })
                    print("✓ DEAL FOUND")
                else:
                    print("✗ No deal")
            except ValueError as e:
                print(f"✗ Error: {str(e)[:50]}...")
                continue
        
        # Display results
        print("\n" + "=" * 80)
        print(f"RESULTS: Found {len(deals_with_profit)} products on DEAL")
        print("=" * 80)
        
        if deals_with_profit:
            for i, product in enumerate(deals_with_profit, 1):
                print(f"\n[{i}] {product['title']}")
                print(f"    Current Price: {product['offered_price']} AED")
                print(f"    Original Price: {product['original_price']} AED")
                print(f"    Profit/Discount: {product['profit']}")
                print(f"    URL: {product['url']}")
            
            # Save results to file
            try:
                with open("noon_deals.json", 'w', encoding='utf-8') as f:
                    json.dump(deals_with_profit, f, indent=2, ensure_ascii=False)
                print(f"\n[OK] Saved {len(deals_with_profit)} deals to noon_deals.json")
            except Exception as e:
                print(f"\n[ERROR] Failed to save to file: {e}")
        else:
            print("\n[*] No products with profit information found.")
    
    except ValueError as e:
        print(f"[ERROR] {e}")