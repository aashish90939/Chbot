# HSRW Chatbot

The **HSRW Chatbot** is a comprehensive tool designed to scrape, process, and interact with data from the HSRW university website. It uses **Scrapy** for web scraping, **ChromaDB** for database storage, and integrates **OpenAI LLM** for intelligent chatbot capabilities, accessible via a **Streamlit GUI**.

---

## 🚀 Features
- **Web Scraping**: Crawl the HSRW university website using Scrapy.
- **Data Processing**: Process scraped markdown data into a structured format for storage.
- **Vector Database**: Store and retrieve data using ChromaDB.
- **GUI with Streamlit**: A user-friendly interface for interacting with the chatbot.
- **OpenAI LLM Integration**: Generate intelligent responses using a language model.

---

## 📂 Project Structure
```plaintext
HSRW_CHATBOT/
├── .idea/                  # Project-specific settings for IDE
├── app/
│   ├── assets/             # Contains image assets for GUI
│   │   ├── ai.png
│   │   ├── image1.png
│   │   ├── image1.svg
│   │   └── user.png
│   ├── config/
│   │   └── CONFIG.py       # Configuration settings
│   ├── frontend/
│   │   └── frontend.py     # GUI implementation with Streamlit
│   ├── helper/
│   │   ├── data_preprocesser.py  # Markdown data processing
│   │   └── vizualization.py      # Visualization tools
│   └── scrapper/
│       └── website_scrapper/    # Scrapy project folder
│           ├── spiders/         # Scrapy spiders for crawling
│           ├── items.py         # Scrapy item definitions
│           ├── pipelines.py     # Scrapy pipelines
│           ├── settings.py      # Scrapy settings
│           └── scrapy.cfg       # Scrapy configuration file
├── .env                     # Environment variables (ignored in Git)
├── .gitignore               # Files and folders ignored by Git
├── Dockerfile               # Docker container setup
├── docker-compose.yml       # Docker Compose setup
├── HSRW_Chatbot.iml         # Project file for IDE
├── requirements.txt         # Python dependencies
├── wait-for-it.sh           # Shell script for service initialization
└── README.md                # Documentation file


🛠️ Technologies Used
Web Scraping: Scrapy
Vector Database: ChromaDB
Frontend: Streamlit
LLM Integration: OpenAI API
Docker: Containerized deployment
#🚀 Getting Started
##Prerequisites
Python 3.8+
Docker (if using containerized deployment)
Installation
1.Clone the repository:
2.Install Python dependencies:
3.Set up your .env file: for apis

#Running the Application
##Option 1: Run Locally
1.	Start the Scrapy spider to crawl the website:
cd app/scrapper/website_scrapper
scrapy crawl <spider_name>
2.	Process the scraped data:
python app/helper/data_preprocesser.py
3.	Launch the chatbot interface:
python app/frontend/frontend.py
##Option 2: Run with Docker
1.	Build the Docker container:
docker-compose build
2.	Start the container:
docker-compose up

![image](https://github.com/user-attachments/assets/66050eb0-f3c6-4489-8ff4-2b4da4608da3)

##📜 License
This project is licensed under @@shish


