"""
Email Extraction Module
Extracts email addresses from HTML content using BeautifulSoup and regex.
"""

import re
from typing import List, Set
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class EmailExtractor:
    """Extracts email addresses from HTML content."""
    
    # Email regex pattern
    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )
    
    # Priority email prefixes (higher priority first)
    PRIORITY_PREFIXES = [
        'contact', 'info', 'support', 'hello', 'sales', 
        'business', 'inquiry', 'general', 'help'
    ]
    
    # Common email patterns to avoid
    EXCLUDE_PATTERNS = [
        'example.com', 'test.com', 'domain.com', 'email.com',
        'yourdomain.com', 'yoursite.com', 'sentry.io',
        'wixpress.com', 'example@', 'test@', 'noreply',
        'no-reply', 'donotreply', 'mailer-daemon'
    ]
    
    def __init__(self, base_url: str = None):
        """
        Initialize EmailExtractor.
        
        Args:
            base_url: Base URL of the website (for domain validation)
        """
        self.base_url = base_url
        self.base_domain = None
        if base_url:
            try:
                parsed = urlparse(base_url)
                self.base_domain = parsed.netloc.replace('www.', '')
            except Exception:
                pass
    
    def extract_emails(self, html_content: str) -> List[str]:
        """
        Extract all email addresses from HTML content.
        
        Args:
            html_content: HTML content as string
            
        Returns:
            List of unique email addresses found
        """
        if not html_content:
            return []
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Get all text content
        text_content = soup.get_text()
        
        # Also check common email attributes
        email_attributes = []
        for tag in soup.find_all(['a', 'span', 'div', 'p']):
            # Check href attributes
            if tag.get('href', '').startswith('mailto:'):
                email = tag.get('href').replace('mailto:', '').strip()
                email_attributes.append(email)
            
            # Check data attributes
            for attr in tag.attrs:
                if 'email' in attr.lower() or 'mail' in attr.lower():
                    value = tag.get(attr, '')
                    if isinstance(value, str) and '@' in value:
                        email_attributes.append(value)
        
        # Find all emails using regex
        emails = set()
        
        # From text content
        text_emails = self.EMAIL_PATTERN.findall(text_content)
        emails.update(text_emails)
        
        # From attributes
        for email_attr in email_attributes:
            matches = self.EMAIL_PATTERN.findall(email_attr)
            emails.update(matches)
        
        # Clean and validate emails
        cleaned_emails = self._clean_emails(list(emails))
        
        return cleaned_emails
    
    def _clean_emails(self, emails: List[str]) -> List[str]:
        """
        Clean and filter email addresses.
        
        Args:
            emails: List of raw email addresses
            
        Returns:
            List of cleaned and validated emails
        """
        cleaned = []
        seen = set()
        
        for email in emails:
            # Convert to lowercase
            email = email.lower().strip()
            
            # Remove common artifacts
            email = email.rstrip('.,;:!?')
            
            # Skip if already seen
            if email in seen:
                continue
            
            # Skip if matches exclude patterns
            if any(pattern in email for pattern in self.EXCLUDE_PATTERNS):
                continue
            
            # Basic validation
            if not self._is_valid_email(email):
                continue
            
            # Domain validation (if base_domain is set)
            if self.base_domain and not self._is_domain_related(email):
                # Still include, but lower priority
                pass
            
            cleaned.append(email)
            seen.add(email)
        
        # Sort by priority
        cleaned = self._prioritize_emails(cleaned)
        
        return cleaned
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        if not email or len(email) < 5:
            return False
        
        if email.count('@') != 1:
            return False
        
        local, domain = email.split('@', 1)
        
        if not local or not domain:
            return False
        
        if '.' not in domain:
            return False
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9._%+-]+$', local):
            return False
        
        return True
    
    def _is_domain_related(self, email: str) -> bool:
        """Check if email domain is related to base domain."""
        if not self.base_domain:
            return True
        
        try:
            email_domain = email.split('@')[1].replace('www.', '')
            base_parts = self.base_domain.split('.')
            email_parts = email_domain.split('.')
            
            # Check if domains match or are related
            if email_domain == self.base_domain:
                return True
            
            # Check for subdomain matches
            if email_domain.endswith('.' + self.base_domain):
                return True
            
            # Check if main domain parts match
            if len(base_parts) >= 2 and len(email_parts) >= 2:
                if base_parts[-2:] == email_parts[-2:]:
                    return True
        except Exception:
            pass
        
        return False
    
    def _prioritize_emails(self, emails: List[str]) -> List[str]:
        """
        Sort emails by priority (contact, info, support first).
        
        Args:
            emails: List of email addresses
            
        Returns:
            Sorted list with priority emails first
        """
        priority_emails = []
        other_emails = []
        
        for email in emails:
            local_part = email.split('@')[0].lower()
            is_priority = any(
                local_part.startswith(prefix) or local_part == prefix
                for prefix in self.PRIORITY_PREFIXES
            )
            
            if is_priority:
                priority_emails.append(email)
            else:
                other_emails.append(email)
        
        # Return priority emails first, then others
        return priority_emails + other_emails
    
    def get_best_email(self, html_content: str) -> str:
        """
        Get the best (highest priority) email from HTML.
        
        Args:
            html_content: HTML content as string
            
        Returns:
            Best email address found, or empty string
        """
        emails = self.extract_emails(html_content)
        return emails[0] if emails else ""

