# 🚀 Automated Contact Finder + Email Sender

A Python-based automation tool that visits company websites, extracts contact emails, and automatically sends personalized messages using Gmail API.

## 📋 Features

- ✅ **Website Automation**: Uses Playwright to visit websites and navigate to contact pages
- ✅ **Email Extraction**: Extracts emails using BeautifulSoup and regex patterns
- ✅ **Gmail API Integration**: Sends emails via Gmail API with OAuth2 authentication
- ✅ **Multiple Storage Formats**: Saves results to CSV, Excel, or SQLite
- ✅ **Batch Processing**: Process multiple companies at once
- ✅ **Comprehensive Logging**: Detailed logs of all operations
- ✅ **Error Handling**: Robust error handling and retry logic

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
cd CompanyEmail
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

### 4. Set Up Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Download the credentials JSON file
5. Save the credentials file as `credentials.json` in the project root

## 📖 Usage

### Basic Usage

#### Process a Single URL

```bash
python main.py --url "https://example.com"
```

#### Process Multiple URLs

```bash
python main.py --urls "https://example.com" "https://another.com" "https://third.com"
```

#### Process URLs from File

Create a text file (`urls.txt`) with one URL per line:

```
https://example.com
https://another.com
https://third.com
```

Then run:

```bash
python main.py --file urls.txt
```

#### Process CSV File

If you have a CSV file with URLs in the first column:

```bash
python main.py --file companies.csv
```

### Advanced Options

#### Extract Emails Without Sending

```bash
python main.py --file urls.txt --no-send
```

#### Custom Email Subject

```bash
python main.py --file urls.txt --subject "Your Custom Subject"
```

#### Custom Email Body

Create a file `email_template.txt` with your email body, then:

```bash
python main.py --file urls.txt --body-file email_template.txt
```

#### Choose Output Format

```bash
# Save only to CSV
python main.py --file urls.txt --format csv

# Save only to Excel
python main.py --file urls.txt --format excel

# Save only to SQLite
python main.py --file urls.txt --format sqlite

# Save to all formats (default)
python main.py --file urls.txt --format all
```

#### Run Browser in Visible Mode

```bash
python main.py --file urls.txt --no-headless
```

### Command Line Arguments

```
--url URL              Single company URL to process
--urls URL [URL ...]   Multiple company URLs to process
--file FILE            File containing URLs (one per line or CSV)
--credentials FILE     Path to Gmail OAuth2 credentials (default: credentials.json)
--no-send              Extract emails but do not send them
--headless             Run browser in headless mode (default: True)
--no-headless          Run browser in visible mode
--format FORMAT        Output format: csv, excel, sqlite, all (default: all)
--subject SUBJECT      Email subject line (default: "Quick Collaboration Inquiry")
--body-file FILE       File containing email body template
```

## 📁 Project Structure

```
CompanyEmail/
├── main.py                 # Main entry point
├── crawler.py              # Website crawling with Playwright
├── extract_email.py        # Email extraction logic
├── send_email.py           # Gmail API email sender
├── storage.py              # Data storage (CSV/Excel/SQLite)
├── requirements.txt        # Python dependencies
├── credentials.json        # Gmail OAuth2 credentials (you need to add this)
├── token.json              # OAuth2 token (auto-generated)
├── utils/
│   ├── __init__.py
│   └── logger.py           # Logging utilities
├── results/                # Output directory (auto-created)
│   ├── results_*.csv
│   ├── results_*.xlsx
│   └── results_*.db
└── README.md
```

## 📊 Output Format

Results are saved with the following columns:

| Column | Description |
|--------|-------------|
| Company | Company URL |
| URL | Final URL visited |
| Email Found | Extracted email address |
| Status | Success/Failed/No Email Found |
| Message ID | Gmail message ID (if sent) |
| Error | Error message (if any) |
| Timestamp | Processing timestamp |

## 🔧 Configuration

### Email Template

The default email template is:

```
Hi,

I hope you're doing well. My name is Sumanth — I came across your work and was really impressed. I'm reaching out to see if there's an opportunity to collaborate, volunteer, or contribute on a project basis.

I have experience in data engineering, automation, and analytics, and I'd be happy to offer support wherever needed.

Thanks,
Sumanth
```

You can customize it by creating a text file and using `--body-file`.

### Contact Page Detection

The crawler automatically tries common contact page paths:
- `/contact`
- `/contact-us`
- `/about`
- `/about-us`
- `/support`
- `/get-in-touch`
- And more...

### Email Priority

The extractor prioritizes emails with these prefixes:
- `contact@`
- `info@`
- `support@`
- `hello@`
- `sales@`

## 🐛 Troubleshooting

### Gmail API Authentication Issues

1. **First Time Setup**: When you run the script for the first time, it will open a browser window for OAuth2 authentication. Complete the authentication flow.

2. **Token Expired**: If you see authentication errors, delete `token.json` and re-authenticate.

3. **Credentials Not Found**: Make sure `credentials.json` is in the project root directory.

### Playwright Issues

If you see browser-related errors:

```bash
playwright install chromium
```

### No Emails Found

- Some websites use JavaScript to load emails dynamically - the crawler waits for dynamic content
- Some websites use contact forms instead of displaying emails
- Check the logs for detailed error messages

### Rate Limiting

The script includes a 1-second delay between requests to avoid rate limiting. For large batches, you may want to increase this delay.

## 📝 Logging

All operations are logged to:
- Console (stdout)
- `company_email.log` file

Logs include:
- URLs being processed
- Emails found
- Send status
- Errors and warnings

## ⚠️ Important Notes

1. **Rate Limiting**: Be respectful of websites. Don't send too many requests too quickly.

2. **Email Sending**: Make sure you comply with:
   - CAN-SPAM Act (US)
   - GDPR (EU)
   - Other applicable email marketing laws

3. **Gmail API Limits**: Gmail API has daily sending limits. Check [Google's documentation](https://developers.google.com/gmail/api/guides/quota) for current limits.

4. **Testing**: Always test with `--no-send` first to verify email extraction works before sending actual emails.

## 🎯 Success Criteria

- ✅ Extracts emails from at least 80% of tested websites
- ✅ Successfully sends emails via Gmail using OAuth2
- ✅ Provides clear logs and error handling
- ✅ Works for at least 50 URLs in one batch

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

Feel free to submit issues or pull requests for improvements!

## 📧 Support

For questions or issues, please check the logs first and review the troubleshooting section above.

---

**Happy Automating! 🚀**

