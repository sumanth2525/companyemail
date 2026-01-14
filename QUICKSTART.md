# ⚡ Quick Start Guide

Get up and running in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

## 2. Set Up Gmail API

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download and save as `credentials.json` in project root

**Detailed instructions**: See `SETUP_GUIDE.md`

## 3. Test It Out

### Extract emails without sending (safe test):

```bash
python main.py --url "https://example.com" --no-send
```

### Send an email (real):

```bash
python main.py --url "https://example.com"
```

## 4. Process Multiple Companies

Create `my_urls.txt`:
```
https://company1.com
https://company2.com
https://company3.com
```

Then run:
```bash
python main.py --file my_urls.txt
```

## Common Commands

```bash
# Single URL
python main.py --url "https://example.com"

# Multiple URLs
python main.py --urls "https://site1.com" "https://site2.com"

# From file
python main.py --file urls.txt

# Test mode (no sending)
python main.py --file urls.txt --no-send

# Custom email
python main.py --file urls.txt --subject "My Subject" --body-file email_template.txt
```

## Need Help?

- Full documentation: `README.md`
- Setup details: `SETUP_GUIDE.md`
- Check logs: `company_email.log`

---

**That's it! You're ready to automate! 🚀**

