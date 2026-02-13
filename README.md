# HighStreet Amazon Deals Scraper - Live Version

An interactive web application that allows you to scrape Amazon UAE deals in real-time from the frontend!

## 🚀 Features

- **Live Scraping**: Enter any Amazon deals URL directly from the web interface
- **Auto-Update**: Deals automatically refresh after scraping completes
- **Smart Filtering**: Only displays valid deals with both original and discounted prices
- **Real-time Progress**: See scraping progress in real-time
- **Search & Filter**: Search through scraped deals instantly
- **Detailed View**: Click any deal for full product details
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile

## 📋 Requirements

- Python 3.7 or higher
- Internet connection

## 🔧 Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ How to Run

1. **Start the server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

3. **Start scraping**:
   - Enter an Amazon deals page URL (e.g., `https://www.amazon.ae/deals`)
   - Press Enter or click "Scrape Deals"
   - Wait for the scraping to complete
   - Deals will automatically appear!

## 💡 Usage Tips

### Finding Amazon Deals URLs

Good URLs to scrape:
- `https://www.amazon.ae/deals` - Today's deals
- `https://www.amazon.ae/gp/goldbox` - Gold Box deals
- Any Amazon category deals page
- Search results pages

### Valid Deals Only

The system automatically filters out products that don't have:
- Original price
- Discounted price
- Actual discount percentage

This ensures you only see **real deals**!

### Search Feature

After scraping, use the search box to filter deals by:
- Product name
- Brand name
- Category
- Description keywords

## 📂 Project Structure

```
amazon_deals_scraper/
│
├── app.py                  # Flask backend server
├── amazon_scraper.py       # Scraping logic
├── index.html              # Frontend interface
├── amazon_deals.json       # Scraped deals storage
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🛠️ How It Works

1. **Frontend**: User enters URL in the web interface
2. **Backend**: Flask server receives request and starts scraper
3. **Scraper**: Extracts deals from Amazon page
4. **Filter**: Only saves deals with valid prices
5. **Storage**: Saves valid deals to JSON file
6. **Display**: Frontend automatically loads and displays new deals

## ⚙️ API Endpoints

- `GET /` - Serves the web interface
- `POST /api/scrape` - Starts scraping process
- `GET /api/status` - Gets current scraping status
- `GET /api/deals` - Gets all valid deals

## 🐛 Troubleshooting

**Server won't start?**
- Make sure port 5000 is not in use
- Check if all dependencies are installed

**Scraping fails?**
- Verify the URL is a valid Amazon.ae URL
- Check your internet connection
- Amazon may have updated their HTML structure

**No deals showing?**
- Make sure the deals have both original and discounted prices
- Try a different Amazon deals page URL

## 📝 Notes

- The scraper respects Amazon's servers with random delays
- Scraping large pages may take several minutes
- Only valid deals (with discounts) are displayed
- All prices are in AED (UAE Dirhams)

## 🔒 Ethical Usage

- Use responsibly and respect Amazon's terms of service
- Don't overload their servers with too many requests
- This tool is for personal use and educational purposes

## 📧 Support

If you encounter any issues, please check:
1. All dependencies are installed
2. You're using a valid Amazon.ae URL
3. Your internet connection is stable

---

**Enjoy finding the best deals! 🎉**

