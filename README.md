# 📊 FLOWTIFY — Product Funnel & Usage Analytics with Slack Alerts & Power BI

FLOWTIFY is a simulated **end-to-end analytics pipeline** for SaaS products, focusing on user onboarding, feature adoption, and A/B test effectiveness. Built in **5 days** using Python and Power BI, this project replicates how real-world growth, product, or analytics teams extract insights and trigger alerts from user behavior data.

---

## 🚀 Project Highlights

- 📥 **Daily data ingestion** from user, funnel, and feature usage logs
- 🔄 **Onboarding funnel analysis** (conversion & drop-offs)
- 🧪 **A/B test evaluation** using statistical z-tests
- 📈 **Feature adoption metrics** (24h adoption, time to first use)
- 🔍 **Retention correlation** with user activity
- ⚠️ **Anomaly detection** in conversion trends (7-day moving avg baseline)
- 🔔 **Slack-style alert system** via `.txt` log files (webhook-free)
- 📅 **Automated daily run** via `papermill` + `schedule`
- 📊 **Interactive Power BI dashboard** for final insights

---

**📁 Folder Structure**

FLOWTIFY/  
├── data/ → Raw CSV data (feature usage, funnel events, users)  
├── analysed\_data/ → Output .csv reports  
├── alerts/ → Slack-style daily alert logs  
├── utils.py → All custom analysis functions  
├── slack\_bot.py → Alert logger (funnel drops, A/B test, anomalies)  
├── main.ipynb → Full execution pipeline  
├── flowtify\_scheduler.py → Daily automation script using papermill  
├── README.md → This file  
└── dashboard.pbix → Power BI dashboard (added after Day 5)

* * *

**▶️ How to Run**

📌 **Note**: I have not yet automated the scheduler, but the `main.ipynb` file contains a ready-to-use code snippet for anyone who wishes to automate the pipeline using `papermill` and `schedule`.
```bash
Open `main.ipynb` in Jupyter Notebook and run all cells.  
```
