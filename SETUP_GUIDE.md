# 🔧 Setup Guide

## Quick Start

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Playwright Browser

```bash
playwright install chromium
```

### Step 3: Set Up Gmail API

#### Option A: Using Google Cloud Console (Recommended)

1. **Create a Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Click "Select a project" > "New Project"
   - Enter a project name (e.g., "CompanyEmail")
   - Click "Create"

2. **Enable Gmail API**
   - In the Google Cloud Console, go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on "Gmail API" and click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - If prompted, configure the OAuth consent screen:
     - User Type: External (unless you have a Google Workspace)
     - App name: "CompanyEmail" (or any name)
     - User support email: Your email
     - Developer contact: Your email
     - Click "Save and Continue"
     - Scopes: Add `https://www.googleapis.com/auth/gmail.send`
     - Click "Save and Continue"
     - Add yourself as a test user
     - Click "Save and Continue"
   - Application type: **Desktop app**
   - Name: "CompanyEmail Client"
   - Click "Create"
   - Click "Download JSON"
   - Rename the downloaded file to `credentials.json`
   - Move it to the project root directory

4. **First Run Authentication**
   - When you run the script for the first time, it will open a browser window
   - Sign in with your Google account
   - Click "Allow" to grant permissions
   - The token will be saved as `token.json` for future use

#### Option B: Using Existing Credentials

If you already have Gmail API credentials:
1. Place your `credentials.json` file in the project root
2. Run the script - it will handle authentication automatically

### Step 4: Test the Setup

#### Test Email Extraction (Without Sending)

```bash
python main.py --url "https://example.com" --no-send
```

This will:
- Visit the website
- Extract emails
- Display results
- **NOT send any emails**

#### Test Full Workflow (With Sending)

```bash
python main.py --url "https://example.com"
```

**⚠️ Warning**: This will send an actual email! Make sure you're ready.

## Troubleshooting

### "credentials.json not found"

- Make sure you've downloaded the OAuth2 credentials from Google Cloud Console
- Place the file in the project root directory (same folder as `main.py`)
- The file should be named exactly `credentials.json`

### "Gmail API not enabled"

- Go to Google Cloud Console > APIs & Services > Library
- Search for "Gmail API" and enable it

### "Token expired" or Authentication Errors

- Delete the `token.json` file
- Run the script again - it will prompt for re-authentication

### Playwright Browser Not Found

```bash
playwright install chromium
```

### Import Errors

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Verification Checklist

- [ ] Python 3.10+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browser installed (`playwright install chromium`)
- [ ] Gmail API enabled in Google Cloud Console
- [ ] `credentials.json` file in project root
- [ ] Test run successful (`python main.py --url "https://example.com" --no-send`)

## Next Steps

Once setup is complete, you can:

1. **Process a single company**:
   ```bash
   python main.py --url "https://company.com"
   ```

2. **Process multiple companies from file**:
   ```bash
   python main.py --file urls.txt
   ```

3. **Customize email template**:
   - Edit `email_template.txt`
   - Use `--body-file email_template.txt`

See `README.md` for full usage instructions.

