"""
Example Usage Script
Demonstrates how to use the automation modules programmatically.
"""

import asyncio
from crawler import WebsiteCrawler
from extract_email import EmailExtractor
from send_email import GmailSender, DEFAULT_EMAIL_TEMPLATE
from storage import ResultStorage


async def example_single_company():
    """Example: Process a single company."""
    print("=" * 60)
    print("Example 1: Processing a Single Company")
    print("=" * 60)
    
    url = "https://example.com"
    
    # Initialize crawler
    crawler = WebsiteCrawler(headless=True)
    
    try:
        # Crawl website
        print(f"Crawling: {url}")
        result = await crawler.crawl_url(url, try_contact_pages=True)
        
        if result['success']:
            print(f"✓ Successfully crawled: {result['final_url']}")
            
            # Extract emails
            extractor = EmailExtractor(base_url=url)
            emails = extractor.extract_emails(result['html'])
            
            if emails:
                print(f"✓ Found {len(emails)} email(s):")
                for email in emails:
                    print(f"  - {email}")
                
                best_email = emails[0]
                print(f"\nBest email: {best_email}")
                
                # Optionally send email (commented out for safety)
                # sender = GmailSender()
                # send_result = sender.send_email(
                #     to=best_email,
                #     subject="Quick Collaboration Inquiry",
                #     body=DEFAULT_EMAIL_TEMPLATE
                # )
                # if send_result['success']:
                #     print(f"✓ Email sent! Message ID: {send_result['message_id']}")
            else:
                print("✗ No emails found")
        else:
            print(f"✗ Failed to crawl: {result.get('error', 'Unknown error')}")
    
    finally:
        await crawler.close()


async def example_multiple_companies():
    """Example: Process multiple companies."""
    print("\n" + "=" * 60)
    print("Example 2: Processing Multiple Companies")
    print("=" * 60)
    
    urls = [
        "https://example.com",
        "https://github.com",
    ]
    
    crawler = WebsiteCrawler(headless=True)
    storage = ResultStorage()
    results = []
    
    try:
        for url in urls:
            print(f"\nProcessing: {url}")
            
            # Crawl
            crawl_result = await crawler.crawl_url(url, try_contact_pages=True)
            
            if not crawl_result['success']:
                results.append({
                    'Company': url,
                    'URL': url,
                    'Email Found': '',
                    'Status': 'Failed',
                    'Error': crawl_result.get('error', 'Unknown error'),
                    'Timestamp': '2024-01-01 00:00:00'
                })
                continue
            
            # Extract emails
            extractor = EmailExtractor(base_url=url)
            emails = extractor.extract_emails(crawl_result['html'])
            
            if emails:
                best_email = emails[0]
                results.append({
                    'Company': url,
                    'URL': crawl_result['final_url'],
                    'Email Found': best_email,
                    'Status': 'Email Found (Not Sent)',
                    'Error': '',
                    'Timestamp': '2024-01-01 00:00:00'
                })
                print(f"  ✓ Found: {best_email}")
            else:
                results.append({
                    'Company': url,
                    'URL': crawl_result['final_url'],
                    'Email Found': '',
                    'Status': 'No Email Found',
                    'Error': '',
                    'Timestamp': '2024-01-01 00:00:00'
                })
                print(f"  ✗ No emails found")
    
    finally:
        await crawler.close()
    
    # Save results
    csv_path = storage.save_to_csv(results)
    print(f"\n✓ Results saved to: {csv_path}")


async def example_custom_email_template():
    """Example: Using a custom email template."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Email Template")
    print("=" * 60)
    
    custom_template = """Hello,

I'm reaching out regarding potential collaboration opportunities.

Best regards,
Your Name"""
    
    print("Custom template:")
    print(custom_template)
    print("\n(Email sending code would go here)")


def example_storage_formats():
    """Example: Different storage formats."""
    print("\n" + "=" * 60)
    print("Example 4: Storage Formats")
    print("=" * 60)
    
    storage = ResultStorage()
    
    sample_results = [
        {
            'Company': 'Example Corp',
            'URL': 'https://example.com',
            'Email Found': 'contact@example.com',
            'Status': 'Success',
            'Message ID': '12345',
            'Error': '',
            'Timestamp': '2024-01-01 00:00:00'
        }
    ]
    
    # Save to all formats
    files = storage.save_all_formats(sample_results)
    
    print("Saved to:")
    for format_type, path in files.items():
        print(f"  {format_type.upper()}: {path}")


async def main():
    """Run all examples."""
    print("\n🚀 Company Email Automation - Example Usage\n")
    
    # Run examples
    await example_single_company()
    await example_multiple_companies()
    await example_custom_email_template()
    example_storage_formats()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nNote: Email sending is commented out for safety.")
    print("Uncomment the email sending code in example_single_company() to test.")


if __name__ == '__main__':
    asyncio.run(main())

