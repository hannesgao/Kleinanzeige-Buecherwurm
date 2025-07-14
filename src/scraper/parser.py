from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from datetime import datetime, timedelta
from loguru import logger
import json

class ListingParser:
    """Parser for Kleinanzeigen listing pages"""
    
    def __init__(self):
        self.soup = None
        
    def parse_search_results(self, html: str) -> List[Dict]:
        """Parse search results page and extract listing URLs and basic info"""
        results = []
        self.soup = BeautifulSoup(html, 'lxml')
        
        try:
            # Find all listing items
            listings = self.soup.find_all('article', class_='aditem')
            
            for listing in listings:
                try:
                    listing_data = {}
                    
                    # Extract URL
                    link = listing.find('a', href=True)
                    if link:
                        listing_data['url'] = link['href']
                        if not listing_data['url'].startswith('http'):
                            listing_data['url'] = f"https://www.kleinanzeigen.de{listing_data['url']}"
                    
                    # Extract title
                    title_elem = listing.find('h2', class_='text-module-begin')
                    if title_elem:
                        listing_data['title'] = title_elem.text.strip()
                    
                    # Extract price
                    price_elem = listing.find('p', class_='aditem-main--middle--price')
                    if price_elem:
                        listing_data['price'] = self.clean_price(price_elem.text)
                    
                    # Extract location
                    location_elem = listing.find('div', class_='aditem-main--top--left')
                    if location_elem:
                        listing_data['location'] = location_elem.text.strip()
                    
                    # Extract date
                    date_elem = listing.find('div', class_='aditem-main--top--right')
                    if date_elem:
                        listing_data['date'] = self.parse_relative_date(date_elem.text.strip())
                    
                    # Extract image
                    img_elem = listing.find('img')
                    if img_elem:
                        listing_data['thumbnail'] = img_elem.get('src') or img_elem.get('data-src')
                    
                    if 'url' in listing_data:
                        results.append(listing_data)
                        
                except Exception as e:
                    logger.debug(f"Error parsing listing item: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
            
        return results
    
    def parse_listing_details(self, html: str) -> Dict:
        """Parse individual listing details from HTML"""
        self.soup = BeautifulSoup(html, 'lxml')
        listing_data = {}
        
        try:
            # Title
            title = self.soup.find('h1', id='viewad-title')
            if title:
                listing_data['title'] = title.text.strip()
            
            # Description
            desc = self.soup.find('p', id='viewad-description-text')
            if desc:
                listing_data['description'] = desc.text.strip()
            
            # Price
            price = self.soup.find('h2', id='viewad-price')
            if price:
                listing_data['price'] = self.clean_price(price.text)
            
            # Location details
            locality = self.soup.find('span', id='viewad-locality')
            if locality:
                listing_data['location'] = locality.text.strip()
                # Extract postal code
                postal_match = re.search(r'\b(\d{5})\b', listing_data['location'])
                if postal_match:
                    listing_data['postal_code'] = postal_match.group(1)
            
            # Seller information
            seller_name = self.soup.find('span', class_='userprofile-name')
            if seller_name:
                listing_data['seller_name'] = seller_name.text.strip()
            
            # Check if commercial seller
            commercial_badge = self.soup.find('span', class_='userbadges-vip')
            listing_data['seller_type'] = 'commercial' if commercial_badge else 'private'
            
            # Extract details box information
            details_box = self.soup.find('div', id='viewad-details')
            if details_box:
                listing_data['details'] = self._parse_details_box(details_box)
            
            # Extract images
            listing_data['images'] = self._extract_image_urls()
            
            # Extract view count
            view_elem = self.soup.find(text=re.compile(r'\d+\s*mal aufgerufen'))
            if view_elem:
                view_match = re.search(r'(\d+)', view_elem)
                if view_match:
                    listing_data['view_count'] = int(view_match.group(1))
            
            # Extract listing ID from URL or page
            listing_id_elem = self.soup.find('meta', {'name': 'ad-id'})
            if listing_id_elem:
                listing_data['listing_id'] = listing_id_elem.get('content')
            
            # Extract date
            date_elem = self.soup.find('span', id='viewad-extra-info')
            if date_elem:
                listing_data['listing_date'] = self._parse_listing_date(date_elem.text)
            
            # Extract breadcrumb categories
            breadcrumbs = self.soup.find_all('span', class_='breadcrump-link')
            if len(breadcrumbs) > 1:
                listing_data['category'] = breadcrumbs[-2].text.strip()
                if len(breadcrumbs) > 2:
                    listing_data['subcategory'] = breadcrumbs[-1].text.strip()
                    
        except Exception as e:
            logger.error(f"Error parsing listing details: {e}")
            
        return listing_data
    
    def _parse_details_box(self, details_box) -> Dict:
        """Parse the details box section"""
        details = {}
        
        try:
            # Find all detail items
            detail_items = details_box.find_all('li', class_='addetailslist--detail')
            
            for item in detail_items:
                label = item.find('span', class_='addetailslist--detail--label')
                value = item.find('span', class_='addetailslist--detail--value')
                
                if label and value:
                    key = label.text.strip().rstrip(':')
                    val = value.text.strip()
                    details[key] = val
                    
        except Exception as e:
            logger.debug(f"Error parsing details box: {e}")
            
        return details
    
    def _extract_image_urls(self) -> List[str]:
        """Extract all image URLs from the page"""
        images = []
        
        try:
            # Method 1: Gallery images
            gallery = self.soup.find('div', class_='galleryimage-large')
            if gallery:
                img_tags = gallery.find_all('img')
                for img in img_tags:
                    src = img.get('src') or img.get('data-src')
                    if src and src not in images:
                        images.append(src)
            
            # Method 2: Thumbnail strip
            thumbnails = self.soup.find_all('img', class_='galleryimage-element')
            for thumb in thumbnails:
                # Get full-size image from data attribute
                full_img = thumb.get('data-imgsrc')
                if full_img and full_img not in images:
                    images.append(full_img)
                    
            # Method 3: Main image
            main_img = self.soup.find('img', id='viewad-image')
            if main_img:
                src = main_img.get('src')
                if src and src not in images:
                    images.append(src)
                    
        except Exception as e:
            logger.debug(f"Error extracting images: {e}")
            
        return images
    
    def clean_price(self, price_str: str) -> float:
        """Clean and convert price string to float"""
        if not price_str:
            return 0.0
            
        price_str = price_str.lower()
        
        # Check for free items
        if any(word in price_str for word in ['verschenken', 'gratis', 'kostenlos', 'free']):
            return 0.0
        
        # Extract numeric value
        # Remove currency symbols and text
        price_str = re.sub(r'[€$£]', '', price_str)
        price_str = re.sub(r'(eur|euro|vb|vhb|festpreis)', '', price_str, flags=re.IGNORECASE)
        
        # Replace German decimal separator
        price_str = price_str.replace('.', '').replace(',', '.')
        
        # Extract first number
        match = re.search(r'(\d+(?:\.\d+)?)', price_str)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return 0.0
                
        return 0.0
    
    def parse_relative_date(self, date_str: str) -> Optional[datetime]:
        """Parse relative date strings like 'Heute', 'Gestern', etc."""
        if not date_str:
            return None
            
        date_str = date_str.lower().strip()
        now = datetime.now()
        
        try:
            if 'heute' in date_str:
                return now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif 'gestern' in date_str:
                return (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif 'vorgestern' in date_str:
                return (now - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                # Try to parse "vor X Tagen" (X days ago)
                days_match = re.search(r'vor\s+(\d+)\s+tag', date_str)
                if days_match:
                    days = int(days_match.group(1))
                    return (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Try to parse "vor X Stunden" (X hours ago)
                hours_match = re.search(r'vor\s+(\d+)\s+stunde', date_str)
                if hours_match:
                    hours = int(hours_match.group(1))
                    return now - timedelta(hours=hours)
                
                # Try to parse "vor X Minuten" (X minutes ago)
                minutes_match = re.search(r'vor\s+(\d+)\s+minute', date_str)
                if minutes_match:
                    minutes = int(minutes_match.group(1))
                    return now - timedelta(minutes=minutes)
                
                # Try standard date format (DD.MM.YYYY)
                date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', date_str)
                if date_match:
                    day, month, year = map(int, date_match.groups())
                    return datetime(year, month, day)
                    
        except Exception as e:
            logger.debug(f"Error parsing date '{date_str}': {e}")
            
        return None
    
    def _parse_listing_date(self, date_text: str) -> Optional[datetime]:
        """Parse listing date from detail page"""
        if not date_text:
            return None
            
        # Remove "Eingestellt am" or similar prefixes
        date_text = re.sub(r'(eingestellt am|online seit|seit)\s*', '', date_text, flags=re.IGNORECASE)
        
        return self.parse_relative_date(date_text)
    
    def extract_contact_info(self, soup_or_html) -> Dict:
        """Extract contact information from listing"""
        if isinstance(soup_or_html, str):
            soup = BeautifulSoup(soup_or_html, 'lxml')
        else:
            soup = soup_or_html
            
        contact_info = {}
        
        try:
            # Extract phone number if visible
            phone_elem = soup.find('span', class_='phoneline-number')
            if phone_elem:
                contact_info['phone'] = phone_elem.text.strip()
            
            # Extract contact name
            contact_name = soup.find('span', class_='text-bold', text=re.compile('Ansprechpartner'))
            if contact_name:
                name_value = contact_name.find_next_sibling('span')
                if name_value:
                    contact_info['contact_name'] = name_value.text.strip()
                    
        except Exception as e:
            logger.debug(f"Error extracting contact info: {e}")
            
        return contact_info