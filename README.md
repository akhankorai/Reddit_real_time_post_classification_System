Image of the Day → MongoDB Atlas → Live Power BI Dashboard (Scheduled Refresh)
📌 Project Overview

This project is an end-to-end data pipeline + analytics system that automatically fetches today’s image (from a public image source/API), stores it in a cloud MongoDB Atlas database, and exposes it to Power BI for a live dashboard experience using scheduled refresh.

The goal is to simulate a real production workflow where data ingestion + cloud storage + BI reporting happens continuously and updates dashboards automatically.

🔗 End-to-End Workflow

Daily Image Fetch (Automated)

A script / Node.js service runs daily (cron / scheduler)

Fetches today’s image + metadata like:

title / category / tags

source url

date

author (if available)

image thumbnail or base64 (optional)

Cloud Storage (MongoDB Atlas)

The fetched record is stored as a document in MongoDB Atlas (cloud)

Each document is timestamped (createdAt, date)

Duplicate prevention logic (avoid saving same image twice)

Backend API Layer (Node.js + Express)

REST endpoints like:

GET /images/today

GET /images?date=...

GET /images/latest

This API acts as the clean data access layer for BI tools and apps

Power BI Integration

Power BI connects to the dataset using:

MongoDB/Atlas connector approach, or

ODBC/Atlas SQL/BI Connector route, or

Web/API connector (Power Query calling your Node API)

Dashboard shows latest image + trends

Scheduled Refresh (Power BI Service)

Report published to Power BI Service

Scheduled refresh enabled (hourly/daily)

Refresh uses a configured gateway if required (common for MongoDB/ODBC connections). 
MongoDB
+2
MongoDB
+2

🏗️ Architecture
Daily Scheduler (Cron / Cloud Scheduler)
           ↓
Image Fetch Service (Node.js/Python)
           ↓
MongoDB Atlas (Cloud)
           ↓
Node.js Express API (Data Access Layer)
           ↓
Power BI Dataset + Dashboard
           ↓
Scheduled Refresh (Power BI Service)

🗄️ MongoDB Atlas Data Model (Example)

Each record saved in MongoDB Atlas includes:

date (today’s date)

image_url

thumbnail_url (optional)

title

category/tags

source

createdAt

This structure makes it easy for Power BI to build visuals like:

Images per day

Category distribution

Latest image card

Source-wise breakdown

Weekly/monthly trends

📊 Power BI Dashboard (Auto Updating)

The dashboard is built on cloud data and includes:

✅ “Today’s Image” Card (latest record)

✅ Daily/weekly image count trend

✅ Category & tags distribution

✅ Source analytics (which provider gives most images)

✅ Date filter for historical navigation

Scheduled refresh ensures dashboards stay updated without manual effort. 
MongoDB
+1

⚙️ Key Technical Highlights

Cloud-native database (MongoDB Atlas)

Automated ingestion pipeline (daily scheduler)

REST API for data sharing (Node.js Express)

Business Intelligence integration (Power BI)

Scheduled refresh pipeline (Power BI Service + gateway when needed) 
MongoDB
+1

🧰 Tech Stack

Node.js + Express (API + ingestion service)

MongoDB Atlas (cloud database)

Power BI (dashboarding + scheduled refresh)

Optional:

Cron / Cloud Scheduler (automation)

Docker (deployment)
