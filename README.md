treamlit Image Classification → MongoDB Atlas → Live Power BI Dashboard (Scheduled Refresh)
📌 Project Overview

This project is an end-to-end cloud-based image analytics and visualization system where users interact through a Streamlit web application to select a specific image category (e.g., Nature, Animals, Technology, Art). Based on the selected category, the system fetches and classifies images, displays them in real time, captures user engagement (likes count), and stores all interaction data in a MongoDB Atlas cloud database.

The stored cloud data is then consumed by Power BI to build a live dashboard that updates automatically using scheduled refresh, simulating a real-world production data pipeline.

🔗 End-to-End Workflow
1️⃣ User Interaction (Streamlit App)

User opens the Streamlit application

Selects a desired image category

Classified images related to that category are displayed

User can like images, generating engagement data

Each interaction triggers a backend update

2️⃣ Image Fetching & Classification

Images are fetched from a public image source / API

A classification model validates or assigns the image category

Only images matching the selected category are shown

Metadata extracted:

Image URL / thumbnail

Category (predicted & selected)

Source

Date & timestamp

3️⃣ Cloud Storage (MongoDB Atlas)

All image metadata and user interaction data are stored in MongoDB Atlas (cloud)

Each record includes:

category

image_url

likes_count

source

createdAt

Duplicate handling to prevent re-storing the same image

Acts as the single source of truth

4️⃣ Backend API Layer (Node.js / Python API)

Streamlit communicates with backend services

REST APIs handle:

Image retrieval by category

Like count updates

Data exposure for analytics

Provides a clean data access layer for BI tools

5️⃣ Power BI Integration

Power BI connects to MongoDB Atlas using:

Atlas SQL / BI Connector, or

Power BI Web API connector

Cloud data is imported into Power BI datasets

Dashboards reflect:

Category-wise image distribution

Likes per image

Most popular categories

Daily / weekly engagement trends

6️⃣ Scheduled Refresh (Power BI Service)

Power BI report published to Power BI Service

Scheduled refresh enabled (hourly / daily)

Optional gateway configuration if required

Dashboards update automatically without manual intervention

🏗️ System Architecture
User (Streamlit UI)
        ↓
Image Fetch + Classification
        ↓
MongoDB Atlas (Cloud Database)
        ↓
Backend API (Node.js / Python)
        ↓
Power BI Dataset & Dashboard
        ↓
Scheduled Refresh (Power BI Service)

🗄️ MongoDB Atlas Data Model (Example)

Each document stored includes:

category

image_url

thumbnail_url (optional)

likes_count

source

createdAt

This schema enables efficient analytics and dashboarding.

📊 Power BI Dashboard (Auto-Updating)

The Power BI dashboard includes:

✅ Category-wise image count

✅ Top liked images

✅ Likes trend over time

✅ Popular categories ranking

✅ Date and category filters

Dashboards stay up-to-date using scheduled refresh, ensuring real-time visibility into user engagement and image trends.
