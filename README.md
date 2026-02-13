# 🛒 Amazon Deals Scraper

A powerful web scraper built with Flask that extracts deals from Amazon UAE, featuring real-time progress tracking and a beautiful UI.

## 🚀 Features

- ✅ Extract Amazon deals with prices, discounts, images, and descriptions
- ✅ Real-time progress bar showing deals scraped
- ✅ Beautiful responsive UI
- ✅ Filter and search deals
- ✅ Export to JSON
- ✅ Rate limiting and error handling

## 📦 Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Scraping:** BeautifulSoup4, Requests
- **Deployment:** Koyeb

---

## 🌐 Deploy to Koyeb (FREE)

### Step 1: Push to GitHub

1. Create a new repository on GitHub
2. Initialize git in your project:
```bash
cd amazon_deals_scraper
git init
git add .
git commit -m "Initial commit: Amazon Deals Scraper"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy on Koyeb

1. **Go to [Koyeb.com](https://www.koyeb.com/)** and sign up (FREE)

2. **Create New App:**
   - Click "Create App"
   - Select "GitHub" as deployment method
   - Connect your GitHub account
   - Select your repository

3. **Configure Settings:**
   - **App Name:** `amazon-deals-scraper` (or any name)
   - **Branch:** `main`
   - **Build Command:** (leave default - auto-detected)
   - **Run Command:** `gunicorn app:app`
   - **Port:** `8000` (Koyeb default)
   - **Instance Type:** Free (Nano)

4. **Environment Variables** (Optional):
   - Click "Add Variable"
   - Add: `FLASK_ENV=production`

5. **Click "Deploy"**

### Step 3: Access Your App

- Your app will be live at: `https://YOUR-APP-NAME.koyeb.app/`
- Wait 2-3 minutes for deployment
- Check logs if any issues

---

## 💻 Local Development

### Prerequisites
- Python 3.12+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd amazon_deals_scraper

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit: `http://localhost:5000`

---

## 📝 Usage

1. **Enter Amazon deals page URL** (e.g., `https://www.amazon.ae/deals`)
2. **Set number of deals** to scrape (recommended: 10-20)
3. **Click "Scrape Deals"**
4. **Watch progress bar** in real-time
5. **Browse and filter** scraped deals

---

## 📂 Project Structure

```
amazon_deals_scraper/
├── app.py                 # Flask backend
├── amazon_scraper.py      # Amazon scraping logic
├── noon_scraper.py        # Noon scraper (disabled)
├── index.html             # Frontend UI
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment config
├── runtime.txt           # Python version
├── amazon_deals.json     # Scraped data
└── README.md             # Documentation
```

---

## ⚙️ Configuration

### Files Already Configured:
- ✅ `Procfile` - Tells Koyeb how to run the app
- ✅ `runtime.txt` - Specifies Python 3.12
- ✅ `requirements.txt` - All dependencies listed
- ✅ `app.py` - PORT environment variable handled

---

## 🔧 Troubleshooting

### Deployment Issues:

**Build fails:**
- Check if all files are committed to git
- Verify `requirements.txt` is in root directory

**App crashes:**
- Check Koyeb logs: Dashboard → Your App → Logs
- Ensure PORT is not hardcoded (use environment variable)

**Scraping fails:**
- Amazon may block cloud IPs occasionally
- Try reducing number of deals
- Add delays between requests

---

## 🛡️ Important Notes

- **Rate Limiting:** Built-in delays prevent IP blocking
- **Cloud Limitations:** Some websites may block cloud server IPs
- **Free Tier:** Koyeb free tier is sufficient for this app
- **Noon Scraper:** Temporarily disabled (can be re-enabled)

---

## 📊 API Endpoints

- `GET /` - Main UI
- `POST /api/scrape` - Start scraping
- `GET /api/status?platform=amazon` - Get scraping status
- `GET /api/deals?platform=amazon` - Get scraped deals

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

## 📄 License

This project is for educational purposes only. Please respect website terms of service when scraping.

---

## 👨‍💻 Author

Built with ❤️ by HighStreet Team

---

## 🔗 Quick Links

- [Koyeb Documentation](https://www.koyeb.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
