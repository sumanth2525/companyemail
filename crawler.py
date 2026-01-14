"""
Website Crawler Module
Uses Playwright to visit websites and extract HTML content.
"""

import asyncio
from typing import List, Optional, Dict
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urljoin, urlparse


class WebsiteCrawler:
    """Crawls websites using Playwright to extract HTML content."""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize WebsiteCrawler.
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
    
    async def _init_browser(self):
        """Initialize Playwright browser."""
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.headless
            )
    
    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    def _get_contact_pages(self, base_url: str) -> List[str]:
        """
        Generate list of potential contact page URLs.
        
        Args:
            base_url: Base website URL
            
        Returns:
            List of potential contact page URLs
        """
        # Ensure URL has scheme
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url
        
        # Remove trailing slash
        base_url = base_url.rstrip('/')
        
        # Common contact page paths
        contact_paths = [
            '/contact',
            '/contact-us',
            '/contactus',
            '/about',
            '/about-us',
            '/aboutus',
            '/support',
            '/get-in-touch',
            '/reach-us',
            '/connect',
            '/',
        ]
        
        urls = []
        for path in contact_paths:
            urls.append(urljoin(base_url, path))
        
        return urls
    
    async def crawl_url(self, url: str, try_contact_pages: bool = True) -> Dict:
        """
        Crawl a single URL and extract HTML content.
        
        Args:
            url: URL to crawl
            try_contact_pages: Whether to try common contact pages if main URL fails
            
        Returns:
            Dictionary with:
            {
                'url': str,
                'html': str or None,
                'success': bool,
                'error': str or None,
                'final_url': str
            }
        """
        await self._init_browser()
        
        # Ensure URL has scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        urls_to_try = [url]
        
        if try_contact_pages:
            urls_to_try.extend(self._get_contact_pages(url))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for u in urls_to_try:
            if u not in seen:
                seen.add(u)
                unique_urls.append(u)
        
        page = await self.browser.new_page()
        
        # Set reasonable timeouts
        page.set_default_timeout(self.timeout)
        
        last_error = None
        
        for try_url in unique_urls:
            try:
                # Navigate to page
                response = await page.goto(
                    try_url,
                    wait_until='networkidle',
                    timeout=self.timeout
                )
                
                if response and response.status == 200:
                    # Wait a bit for dynamic content
                    await page.wait_for_timeout(2000)
                    
                    # Get HTML content
                    html = await page.content()
                    
                    final_url = page.url
                    
                    await page.close()
                    
                    return {
                        'url': url,
                        'html': html,
                        'success': True,
                        'error': None,
                        'final_url': final_url
                    }
                else:
                    last_error = f"HTTP {response.status if response else 'No response'}"
            
            except PlaywrightTimeoutError:
                last_error = "Page load timeout"
                continue
            
            except Exception as e:
                last_error = str(e)
                continue
        
        await page.close()
        
        return {
            'url': url,
            'html': None,
            'success': False,
            'error': last_error or "Failed to load page",
            'final_url': url
        }
    
    async def crawl_multiple(self, urls: List[str], 
                            try_contact_pages: bool = True) -> List[Dict]:
        """
        Crawl multiple URLs.
        
        Args:
            urls: List of URLs to crawl
            try_contact_pages: Whether to try common contact pages
            
        Returns:
            List of crawl results
        """
        results = []
        
        for url in urls:
            result = await self.crawl_url(url, try_contact_pages)
            results.append(result)
        
        return results


# Convenience function for synchronous use
def crawl_url_sync(url: str, headless: bool = True, 
                  try_contact_pages: bool = True) -> Dict:
    """
    Synchronous wrapper for crawl_url.
    
    Args:
        url: URL to crawl
        headless: Run browser in headless mode
        try_contact_pages: Whether to try common contact pages
        
    Returns:
        Crawl result dictionary
    """
    async def _crawl():
        crawler = WebsiteCrawler(headless=headless)
        try:
            return await crawler.crawl_url(url, try_contact_pages)
        finally:
            await crawler.close()
    
    return asyncio.run(_crawl())


def crawl_multiple_sync(urls: List[str], headless: bool = True,
                       try_contact_pages: bool = True) -> List[Dict]:
    """
    Synchronous wrapper for crawl_multiple.
    
    Args:
        urls: List of URLs to crawl
        headless: Run browser in headless mode
        try_contact_pages: Whether to try common contact pages
        
    Returns:
        List of crawl results
    """
    async def _crawl():
        crawler = WebsiteCrawler(headless=headless)
        try:
            return await crawler.crawl_multiple(urls, try_contact_pages)
        finally:
            await crawler.close()
    
    return asyncio.run(_crawl())

