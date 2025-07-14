from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from loguru import logger
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote
import json
from ..utils.retry import retry_on_exception, NetworkError, ParseError

class KleinanzeigenCrawler:
    """Main crawler class for Kleinanzeigen.de using Selenium"""
    
    BASE_URL = "https://www.kleinanzeigen.de"
    
    def __init__(self, config: Dict):
        self.config = config
        self.driver = None
        self.wait = None
        self.setup_driver()
        
    def setup_driver(self):
        """Initialize Chrome driver with options"""
        options = Options()
        
        # Set window size
        window_size = self.config.get('window_size', '1920,1080')
        options.add_argument(f'--window-size={window_size}')
        
        # Set user agent
        user_agent = self.config.get('user_agent')
        if user_agent:
            options.add_argument(f'--user-agent={user_agent}')
        
        # Headless mode
        if self.config.get('headless', False):
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            
        # Other optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Set timeouts
        self.driver.set_page_load_timeout(self.config.get('page_load_timeout', 30))
        self.driver.implicitly_wait(self.config.get('implicit_wait', 10))
        
        # Initialize wait
        self.wait = WebDriverWait(self.driver, self.config.get('implicit_wait', 10))
        
        logger.info("Chrome driver initialized successfully")
        
    @retry_on_exception(
        max_attempts=3,
        delay=2.0,
        backoff=2.0,
        exceptions=(TimeoutException, WebDriverException)
    )
    def search_books(self, search_params: Dict) -> List[str]:
        """Search for books and return listing URLs"""
        listing_urls = []
        
        try:
            # Build search URL
            category = search_params.get('category', 'antike-buecher')
            location = search_params.get('location', 'Karlsruhe')
            radius = search_params.get('radius_km', 20)
            max_price = search_params.get('max_price', 0)
            
            # Start with category page
            search_url = f"{self.BASE_URL}/s-{category}/k0"
            
            logger.info(f"Navigating to search URL: {search_url}")
            self.driver.get(search_url)
            self._random_delay()
            
            # Handle cookie consent if present
            self._handle_cookie_consent()
            
            # Set location
            self._set_location(location, radius)
            
            # Set price filter (free items)
            if max_price == 0:
                self._set_free_items_filter()
            
            # Search for each keyword
            keywords = search_params.get('keywords', [])
            for keyword in keywords:
                logger.info(f"Searching for keyword: {keyword}")
                urls = self._search_keyword(keyword)
                listing_urls.extend(urls)
                
            # Remove duplicates
            listing_urls = list(set(listing_urls))
            logger.info(f"Found {len(listing_urls)} unique listings")
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise
            
        return listing_urls
    
    def _handle_cookie_consent(self):
        """Handle cookie consent popup if present"""
        try:
            # Look for common cookie consent buttons
            consent_buttons = [
                "//button[contains(text(), 'Alle akzeptieren')]",
                "//button[contains(text(), 'Akzeptieren')]",
                "//button[@id='gdpr-banner-accept']"
            ]
            
            for xpath in consent_buttons:
                try:
                    button = self.driver.find_element(By.XPATH, xpath)
                    if button.is_displayed():
                        button.click()
                        logger.info("Cookie consent accepted")
                        self._random_delay(1, 2)
                        break
                except NoSuchElementException:
                    continue
                    
        except Exception as e:
            logger.debug(f"No cookie consent found or already accepted: {e}")
    
    def _set_location(self, location: str, radius: int):
        """Set search location and radius"""
        try:
            # Find location input
            location_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "site-search-area"))
            )
            location_input.clear()
            location_input.send_keys(location)
            self._random_delay(1, 2)
            
            # Wait for suggestions and click first one
            suggestion = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".autocomplete-suggestion"))
            )
            suggestion.click()
            
            # Set radius
            radius_select = self.driver.find_element(By.ID, "site-search-rad")
            radius_select.click()
            
            # Select radius option
            radius_option = self.driver.find_element(
                By.XPATH, f"//option[@value='{radius}']"
            )
            radius_option.click()
            
            logger.info(f"Location set to {location} with {radius}km radius")
            
        except Exception as e:
            logger.error(f"Error setting location: {e}")
    
    def _set_free_items_filter(self):
        """Set filter for free items only"""
        try:
            # Click on price filter
            price_filter = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Preis')]"))
            )
            price_filter.click()
            self._random_delay(1, 2)
            
            # Select "Zu verschenken" option
            free_option = self.driver.find_element(
                By.XPATH, "//label[contains(text(), 'Zu verschenken')]"
            )
            free_option.click()
            
            # Apply filter
            apply_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Anwenden')]"
            )
            apply_button.click()
            
            logger.info("Free items filter applied")
            
        except Exception as e:
            logger.error(f"Error setting free items filter: {e}")
    
    def _search_keyword(self, keyword: str) -> List[str]:
        """Search for specific keyword and collect listing URLs"""
        urls = []
        
        try:
            # Find search input
            search_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "site-search-query"))
            )
            search_input.clear()
            search_input.send_keys(keyword)
            
            # Submit search
            search_button = self.driver.find_element(
                By.CSS_SELECTOR, "button[type='submit']"
            )
            search_button.click()
            
            self._random_delay(2, 3)
            
            # Collect listings from multiple pages
            page = 1
            max_pages = self.config.get('max_pages', 50)
            
            while page <= max_pages:
                logger.info(f"Processing page {page} for keyword '{keyword}'")
                
                # Get listing URLs from current page
                listings = self.driver.find_elements(
                    By.CSS_SELECTOR, "article.aditem"
                )
                
                for listing in listings:
                    try:
                        link = listing.find_element(By.CSS_SELECTOR, "a[href]")
                        url = link.get_attribute("href")
                        if url and url.startswith("http"):
                            urls.append(url)
                    except Exception as e:
                        logger.debug(f"Error extracting URL: {e}")
                
                # Check for next page
                try:
                    next_button = self.driver.find_element(
                        By.CSS_SELECTOR, "a.pagination-next"
                    )
                    if next_button.is_enabled():
                        next_button.click()
                        self._random_delay(2, 3)
                        page += 1
                    else:
                        break
                except NoSuchElementException:
                    logger.info("No more pages available")
                    break
                    
        except Exception as e:
            logger.error(f"Error searching keyword '{keyword}': {e}")
            
        return urls
    
    @retry_on_exception(
        max_attempts=3,
        delay=2.0,
        backoff=2.0,
        exceptions=(TimeoutException, WebDriverException, NetworkError)
    )
    def get_listing_details(self, listing_url: str) -> Optional[Dict]:
        """Get detailed information from a listing page"""
        try:
            logger.info(f"Fetching listing: {listing_url}")
            self.driver.get(listing_url)
            self._random_delay()
            
            # Wait for page to load
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1#viewad-title"))
                )
            except TimeoutException:
                logger.error(f"Timeout waiting for listing page to load: {listing_url}")
                raise NetworkError(f"Failed to load listing page: {listing_url}")
            
            listing_data = {
                'listing_url': listing_url,
                'listing_id': self._extract_listing_id(listing_url)
            }
            
            # Extract basic information
            listing_data['title'] = self._safe_find_text("h1#viewad-title")
            listing_data['description'] = self._safe_find_text("#viewad-description-text")
            listing_data['price'] = self._extract_price()
            
            # Extract location
            listing_data['location'] = self._safe_find_text("#viewad-locality")
            listing_data['postal_code'] = self._extract_postal_code()
            
            # Extract seller info
            listing_data['seller_name'] = self._safe_find_text(".userprofile-name")
            listing_data['seller_type'] = self._extract_seller_type()
            
            # Extract dates and views
            listing_data['listing_date'] = self._extract_date()
            listing_data['view_count'] = self._extract_views()
            
            # Extract images
            listing_data['image_urls'] = self._extract_images()
            listing_data['thumbnail_url'] = listing_data['image_urls'][0] if listing_data['image_urls'] else None
            
            # Extract contact info
            listing_data['phone_number'] = self._extract_phone()
            
            # Extract category
            breadcrumbs = self.driver.find_elements(By.CSS_SELECTOR, ".breadcrump-link")
            if len(breadcrumbs) > 1:
                listing_data['category'] = breadcrumbs[-2].text
                listing_data['subcategory'] = breadcrumbs[-1].text if len(breadcrumbs) > 2 else None
            
            return listing_data
            
        except Exception as e:
            logger.error(f"Error fetching listing {listing_url}: {e}")
            return None
    
    def _extract_listing_id(self, url: str) -> str:
        """Extract listing ID from URL"""
        try:
            # URL format: .../s-anzeige/title/id
            parts = url.split('/')
            return parts[-1]
        except:
            return url.split('/')[-1][:100]  # Fallback
    
    def _safe_find_text(self, selector: str, by: By = By.CSS_SELECTOR) -> Optional[str]:
        """Safely find and extract text from element"""
        try:
            element = self.driver.find_element(by, selector)
            return element.text.strip()
        except NoSuchElementException:
            return None
    
    def _extract_price(self) -> float:
        """Extract price from listing"""
        try:
            price_elem = self.driver.find_element(By.CSS_SELECTOR, "#viewad-price")
            price_text = price_elem.text.lower()
            
            if "verschenken" in price_text or "gratis" in price_text:
                return 0.0
            
            # Extract numeric price
            import re
            price_match = re.search(r'(\d+(?:\.\d+)?)', price_text.replace(',', '.'))
            if price_match:
                return float(price_match.group(1))
                
        except:
            pass
        return 0.0
    
    def _extract_postal_code(self) -> Optional[str]:
        """Extract postal code from location"""
        try:
            location = self._safe_find_text("#viewad-locality")
            if location:
                import re
                match = re.search(r'\b(\d{5})\b', location)
                if match:
                    return match.group(1)
        except:
            pass
        return None
    
    def _extract_seller_type(self) -> str:
        """Determine if seller is private or commercial"""
        try:
            commercial_badge = self.driver.find_element(
                By.CSS_SELECTOR, ".userbadges-vip"
            )
            return "commercial"
        except NoSuchElementException:
            return "private"
    
    def _extract_date(self) -> Optional[str]:
        """Extract listing date"""
        try:
            date_elem = self.driver.find_element(By.CSS_SELECTOR, "#viewad-extra-info span")
            date_text = date_elem.text
            # Parse German date format
            from datetime import datetime
            import locale
            try:
                locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
            except:
                pass
            # Return raw date string for now
            return date_text
        except:
            return None
    
    def _extract_views(self) -> Optional[int]:
        """Extract view count"""
        try:
            views_elem = self.driver.find_element(
                By.XPATH, "//span[contains(text(), 'mal aufgerufen')]"
            )
            import re
            match = re.search(r'(\d+)', views_elem.text)
            if match:
                return int(match.group(1))
        except:
            pass
        return None
    
    def _extract_images(self) -> List[str]:
        """Extract all image URLs"""
        images = []
        try:
            # Click on main image to open gallery
            main_image = self.driver.find_element(By.CSS_SELECTOR, "#viewad-image")
            main_image.click()
            self._random_delay(1, 2)
            
            # Get all gallery images
            gallery_images = self.driver.find_elements(
                By.CSS_SELECTOR, ".gallery-img img"
            )
            
            for img in gallery_images:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src:
                    images.append(src)
                    
            # Close gallery
            close_button = self.driver.find_element(
                By.CSS_SELECTOR, ".icon-close-white"
            )
            close_button.click()
            
        except:
            # Fallback: try to get main image
            try:
                main_img = self.driver.find_element(By.CSS_SELECTOR, "#viewad-image img")
                src = main_img.get_attribute("src")
                if src:
                    images.append(src)
            except:
                pass
                
        return images
    
    def _extract_phone(self) -> Optional[str]:
        """Extract phone number if available"""
        try:
            # Click on phone reveal button
            phone_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Telefonnummer anzeigen')]"
            )
            phone_button.click()
            self._random_delay(1, 2)
            
            # Get revealed phone number
            phone_elem = self.driver.find_element(
                By.CSS_SELECTOR, ".phoneline-number"
            )
            return phone_elem.text.strip()
            
        except:
            return None
    
    def _random_delay(self, min_seconds: float = None, max_seconds: float = None):
        """Add random delay to avoid detection"""
        if min_seconds is None:
            min_seconds = self.config.get('delay_between_requests', 3) * 0.5
        if max_seconds is None:
            max_seconds = self.config.get('delay_between_requests', 3) * 1.5
            
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")