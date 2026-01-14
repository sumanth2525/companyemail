"""
Main Entry Point
Automated Contact Finder + Email Sender
"""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from crawler import WebsiteCrawler
from extract_email import EmailExtractor
from send_email import GmailSender, DEFAULT_EMAIL_TEMPLATE
from storage import ResultStorage
from utils.logger import setup_logger


class CompanyEmailAutomation:
    """Main automation class that orchestrates the entire process."""
    
    def __init__(self, 
                 credentials_file: str = 'credentials.json',
                 send_emails: bool = True,
                 headless: bool = True,
                 email_subject: str = 'Quick Collaboration Inquiry',
                 email_body: str = None):
        """
        Initialize the automation system.
        
        Args:
            credentials_file: Path to Gmail OAuth2 credentials
            send_emails: Whether to actually send emails (False for testing)
            headless: Run browser in headless mode
            email_subject: Subject line for emails
            email_body: Email body template (uses default if None)
        """
        self.logger = setup_logger()
        self.send_emails = send_emails
        self.email_subject = email_subject
        self.email_body = email_body or DEFAULT_EMAIL_TEMPLATE
        
        # Initialize components
        self.crawler = None
        self.email_sender = None
        
        if send_emails:
            try:
                self.email_sender = GmailSender(credentials_file=credentials_file)
                sender_email = self.email_sender.get_sender_email()
                self.logger.info(f"Gmail API authenticated successfully")
                self.logger.info(f"Emails will be sent from: {sender_email}")
                print(f"\n✓ Gmail API authenticated")
                print(f"✓ Emails will be sent from: {sender_email}\n")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gmail sender: {e}")
                self.logger.warning("Continuing without email sending capability")
                self.send_emails = False
        
        self.storage = ResultStorage()
    
    async def process_company(self, url: str) -> Dict:
        """
        Process a single company URL.
        
        Args:
            url: Company website URL
            
        Returns:
            Result dictionary with all processing information
        """
        self.logger.info(f"Processing: {url}")
        
        result = {
            'Company': url,
            'URL': url,
            'Email Found': '',
            'Status': 'Failed',
            'Message ID': '',
            'Error': '',
            'Sender Email': self.email_sender.get_sender_email() if self.email_sender else '',
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Initialize crawler if needed
            if not self.crawler:
                self.crawler = WebsiteCrawler(headless=True)
            
            # Crawl website
            crawl_result = await self.crawler.crawl_url(url, try_contact_pages=True)
            
            if not crawl_result['success']:
                result['Error'] = f"Crawl failed: {crawl_result.get('error', 'Unknown error')}"
                self.logger.warning(f"Failed to crawl {url}: {result['Error']}")
                return result
            
            # Extract emails
            extractor = EmailExtractor(base_url=url)
            emails = extractor.extract_emails(crawl_result['html'])
            
            if not emails:
                result['Error'] = "No email addresses found"
                result['Status'] = 'No Email Found'
                self.logger.warning(f"No emails found for {url}")
                return result
            
            # Get best email
            best_email = emails[0]
            result['Email Found'] = best_email
            self.logger.info(f"Found email: {best_email} for {url}")
            
            # Send email if enabled
            if self.send_emails and self.email_sender:
                send_result = self.email_sender.send_email(
                    to=best_email,
                    subject=self.email_subject,
                    body=self.email_body
                )
                
                if send_result['success']:
                    result['Status'] = 'Success'
                    result['Message ID'] = send_result.get('message_id', '')
                    self.logger.info(f"Email sent successfully to {best_email}")
                else:
                    result['Status'] = 'Send Failed'
                    result['Error'] = send_result.get('error', 'Unknown error')
                    self.logger.error(f"Failed to send email to {best_email}: {result['Error']}")
            else:
                result['Status'] = 'Email Found (Not Sent)'
                self.logger.info(f"Email found but not sent (send_emails={self.send_emails})")
        
        except Exception as e:
            result['Error'] = f"Unexpected error: {str(e)}"
            result['Status'] = 'Error'
            self.logger.error(f"Error processing {url}: {e}", exc_info=True)
        
        return result
    
    async def process_companies(self, urls: List[str]) -> List[Dict]:
        """
        Process multiple company URLs.
        
        Args:
            urls: List of company website URLs
            
        Returns:
            List of result dictionaries
        """
        results = []
        total = len(urls)
        
        self.logger.info(f"Starting processing of {total} companies")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Processing {i}/{total}: {url}")
            result = await self.process_company(url)
            results.append(result)
            
            # Small delay to avoid rate limiting
            if i < total:
                await asyncio.sleep(1)
        
        return results
    
    async def close(self):
        """Clean up resources."""
        if self.crawler:
            await self.crawler.close()
    
    def save_results(self, results: List[Dict], format: str = 'all') -> Dict[str, str]:
        """
        Save results to file(s).
        
        Args:
            results: List of result dictionaries
            format: 'csv', 'excel', 'sqlite', or 'all'
            
        Returns:
            Dictionary with paths to saved files
        """
        if format == 'csv':
            path = self.storage.save_to_csv(results)
            return {'csv': path}
        elif format == 'excel':
            path = self.storage.save_to_excel(results)
            return {'excel': path}
        elif format == 'sqlite':
            path = self.storage.save_to_sqlite(results)
            return {'sqlite': path}
        else:  # 'all'
            return self.storage.save_all_formats(results)


def load_urls_from_file(filepath: str) -> List[str]:
    """
    Load URLs from a file (one per line or CSV).
    
    Args:
        filepath: Path to file containing URLs
        
    Returns:
        List of URLs
    """
    urls = []
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Try CSV first
    if filepath.endswith('.csv'):
        import csv
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header if present
            for row in reader:
                if row:
                    url = row[0].strip()
                    if url:
                        urls.append(url)
    else:
        # Plain text file (one URL per line)
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):
                    urls.append(url)
    
    return urls


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Automated Contact Finder + Email Sender',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single URL
  python main.py --url "https://example.com"
  
  # Process multiple URLs
  python main.py --urls "https://example.com" "https://another.com"
  
  # Process URLs from file
  python main.py --file urls.txt
  
  # Process without sending emails (testing)
  python main.py --file urls.txt --no-send
  
  # Save only to CSV
  python main.py --file urls.txt --format csv
        """
    )
    
    parser.add_argument('--url', type=str, help='Single company URL to process')
    parser.add_argument('--urls', nargs='+', help='Multiple company URLs to process')
    parser.add_argument('--file', type=str, help='File containing URLs (one per line or CSV)')
    parser.add_argument('--credentials', type=str, default='credentials.json',
                       help='Path to Gmail OAuth2 credentials file')
    parser.add_argument('--no-send', action='store_true',
                       help='Extract emails but do not send them')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode (default: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                       help='Run browser in visible mode')
    parser.add_argument('--format', type=str, default='all',
                       choices=['csv', 'excel', 'sqlite', 'all'],
                       help='Output format (default: all)')
    parser.add_argument('--subject', type=str, default='Quick Collaboration Inquiry',
                       help='Email subject line')
    parser.add_argument('--body-file', type=str,
                       help='File containing email body template')
    
    args = parser.parse_args()
    
    # Collect URLs
    urls = []
    
    if args.url:
        urls.append(args.url)
    
    if args.urls:
        urls.extend(args.urls)
    
    if args.file:
        file_urls = load_urls_from_file(args.file)
        urls.extend(file_urls)
    
    if not urls:
        parser.print_help()
        print("\nError: No URLs provided. Use --url, --urls, or --file")
        sys.exit(1)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    # Load email body if provided
    email_body = None
    if args.body_file:
        with open(args.body_file, 'r', encoding='utf-8') as f:
            email_body = f.read()
    
    # Initialize automation
    automation = CompanyEmailAutomation(
        credentials_file=args.credentials,
        send_emails=not args.no_send,
        headless=args.headless,
        email_subject=args.subject,
        email_body=email_body
    )
    
    try:
        # Process companies
        results = await automation.process_companies(unique_urls)
        
        # Save results
        saved_files = automation.save_results(results, format=args.format)
        
        # Print summary
        print("\n" + "="*60)
        print("PROCESSING SUMMARY")
        print("="*60)
        total = len(results)
        success = sum(1 for r in results if r['Status'] == 'Success')
        no_email = sum(1 for r in results if r['Status'] == 'No Email Found')
        failed = total - success - no_email
        
        print(f"Total Companies: {total}")
        print(f"Successfully Sent: {success}")
        print(f"No Email Found: {no_email}")
        print(f"Failed: {failed}")
        print("\nResults saved to:")
        for format_type, path in saved_files.items():
            print(f"  {format_type.upper()}: {path}")
        print("="*60)
        
    finally:
        await automation.close()


if __name__ == '__main__':
    asyncio.run(main())

