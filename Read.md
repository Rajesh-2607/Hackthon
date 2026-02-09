# 🔍 Hybrid Fake Social Media Account Detection System

> 🚀 Production-Ready AI System for Detecting Fake, Bot & Scam Social
> Media Accounts\
> Built with **XGBoost (ML)** + **FastAPI (Backend)** + **React
> (Frontend)**

------------------------------------------------------------------------

## 📌 Problem Statement

Fake and bot accounts on social media platforms are used for:

-   Financial scams
-   Phishing & crypto fraud
-   Identity impersonation
-   Misinformation campaigns
-   Artificial engagement manipulation

Traditional rule-based systems fail to scale and adapt.

This project introduces a **Hybrid AI-Based Detection System** combining
behavioral machine learning and scalable API architecture to detect fake
accounts efficiently.

------------------------------------------------------------------------

## 🏗 System Architecture

React Frontend → FastAPI Backend → XGBoost Model (Inference)

------------------------------------------------------------------------

## 🧠 Machine Learning Model

### Algorithm: XGBoost Classifier

The system uses **XGBoost Gradient Boosting** for high-performance
classification.

### Dataset Structure

-   `train.csv` → Used for model training
-   `test.csv` → Used for evaluation & validation

### Feature Examples

-   followers_count\
-   following_count\
-   follower_following_ratio\
-   account_age_days\
-   post_frequency\
-   engagement_rate\
-   bio_length\
-   has_profile_pic\
-   has_url\
-   username_digit_ratio\
-   is_verified

------------------------------------------------------------------------

## ⚙️ ML Pipeline

1.  Data Cleaning\
2.  Feature Engineering\
3.  Model Training (XGBoost)\
4.  Model Evaluation\
5.  Model Serialization (`xgboost_model.pkl`)\
6.  FastAPI loads model for inference

------------------------------------------------------------------------

## 📊 Evaluation Metrics

-   Accuracy\
-   Precision\
-   Recall\
-   F1 Score\
-   ROC-AUC Score

------------------------------------------------------------------------

## 📁 Project Structure

fake-account-detection/

backend/ - main.py - model/ - train_model.py - xgboost_model.pkl -
scaler.pkl - schemas.py - utils.py

frontend/ - src/ - package.json

data/ - train.csv - test.csv

requirements.txt README.md

------------------------------------------------------------------------

## 🚀 Backend Setup (FastAPI)

``` bash
cd backend
pip install -r requirements.txt
python model/train_model.py
uvicorn main:app --reload
```

API Docs: http://localhost:8000/docs

------------------------------------------------------------------------

## 💻 Frontend Setup (React)

``` bash
cd frontend
npm install
npm start
```

Frontend runs at: http://localhost:3000

------------------------------------------------------------------------

## 🌐 API Endpoint Example

POST /predict

Request:

{ "followers_count": 120, "following_count": 5400, "account_age_days":
15, "post_frequency": 25, "engagement_rate": 0.3, "bio_length": 20,
"has_profile_pic": 0, "has_url": 1, "username_digit_ratio": 0.5,
"is_verified": 0 }

Response:

{ "risk_score": 0.87, "prediction": "Fake Account", "confidence": "High"
}

------------------------------------------------------------------------

## 🔥 Key Features

-   High-speed inference
-   Production-ready API
-   Modular architecture
-   Scalable deployment ready

------------------------------------------------------------------------

## 🚀 Deployment Options

Backend: Render / Railway / AWS / Docker\
Frontend: Vercel / Netlify

------------------------------------------------------------------------

## 👨‍💻 Author

Rajesh S\
AI & Data Science Student

------------------------------------------------------------------------

## 📄 License

MIT License
