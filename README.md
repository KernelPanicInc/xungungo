# 📈 Xungungo

**Xungungo** is a desktop application (built with [Streamlit](https://streamlit.io/)) that makes it dead‑simple to explore stocks, overlay technical indicators and keep an eye on market news — all through an intuitive point‑and‑click interface.

---

## 🧭 What can I do with Xungungo?

- 🔍 **Look up** any stock by its ticker (AAPL, MSFT, TSLA…).
- 📊 **Plot** interactive candlestick & volume charts instantly.
- 📈 **Add indicators** such as SMA, RSI, MACD…and more.
- 📰 **Read the latest headlines** without leaving the app.
- 🧩 **Enable plugins** for screeners, dark‑pool flow, forecasting, and other views.

---

## 🚀 Quick install (Windows)

| | |
|---|---|
| **1. Download** | Go to the project **Releases** tab and grab the latest `Xungungo.zip`. |
| **2. Run** | Double‑click the installer and follow the wizard (Python is embedded — nothing else to install). |
| **3. Launch** | A shortcut appears in your Start Menu. Fire it up and start exploring! |

> That’s it — no command line required.

---

## ⚙️ Manual install (advanced / macOS & Linux)

### Prerequisites

* Python ≥ 3.9
* (Optional) Git, if you prefer cloning over downloading ZIPs.

### Steps

```bash
# 1. Clone or download the repo
$ git clone https://github.com/your‑username/xungungo.git
$ cd xungungo

# 2. (Optional) create & activate a virtual environment
$ python -m venv venv
$ source venv/bin/activate   # on Linux/macOS
# .\venv\Scripts\activate  # on Windows PowerShell

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Run the app
$ streamlit run app/Dashboard.py
```

Your default browser will open automatically.

---

## 🧩 Built‑in plugins

| Plugin | What it does |
| --- | --- |
| **Charts** | Main candlestick + volume view |
| **SMA (3 moving averages)** | Overlay up to three configurable moving averages |
| **Screeners** | Surf lists of stocks that meet custom criteria |
| **Dark Pools** | Spot unusual dark‑pool activity |
| **News (Bloomberg, etc.)** | Pull in the freshest market headlines |

> The list keeps growing — check the sidebar to see what’s new.

---

## 📸 Screenshots

> _Coming soon — here we’ll drop images of the dashboard, plugins and charting UI so you can preview the look & feel._

---

## 🖥️ Core dependencies (manual mode)

* **streamlit** – UI layer
* **yfinance** – historical & real‑time market data
* **streamlit‑lightweight‑charts** – TradingView‑style interactive charts
* **pandas** & **numpy** – data wrangling

See [`requirements.txt`](./requirements.txt) for the full list.

---

## 🙌 Contributing

Have an idea for a plugin, found a bug or want to improve the docs? **PRs are welcome!**

1. Open an _Issue_ outlining your suggestion or bug.
2. _Fork_ the repo, create a branch (`git checkout -b feature/my‑feature`), commit your changes and open a _Pull Request_.

---

## 📄 License

Xungungo is distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

