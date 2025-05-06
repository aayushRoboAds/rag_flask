# 📘 API Documentation – LangChain Excel RAG Flask App

Base URL:  
http://<your-server-ip>:5001

---

## 📥 `/adduser` – Upload Excel and Create Vector Store

**Method:** POST  
**Content-Type:** multipart/form-data

Form Fields:
- file: Excel file (.xlsx or .xls)
- userid: Unique user ID

Response:
- 200 OK
{ "message": "File uploaded and vector store created successfully" }

- 400 Bad Request
{ "error": "Missing file or userid" }

- 500 Internal Server Error
{ "error": "<error details>" }

---

## ✏️ `/modifyuser` – Replace User File and Rebuild Vector Store

**Method:** POST  
**Content-Type:** multipart/form-data

Form Fields:
- file: New Excel file
- userid: User ID

Response:
- 200 OK
{ "message": "File uploaded and vector store created successfully" }

- 400 / 500
{ "error": "<error details>" }

---

## ❌ `/deleteuser` – Delete User and Data

**Method:** POST  
**Content-Type:** application/x-www-form-urlencoded

Form Fields:
- userid: User ID

Response:
- 200 OK
{ "message": "User <userid> deleted successfully" }

- 404 Not Found
{ "error": "User folder does not exist" }

- 400 / 500
{ "error": "<error details>" }

---

## 📄 `/viewuserexcelfiles` – View Uploaded Excel Files for a User

**Method:** POST  
**Content-Type:** application/x-www-form-urlencoded

Form Fields:
- userid: User ID

Response:
- 200 OK
{ "files": ["example.xlsx", "sample.xls"] }

- 404 Not Found
{ "error": "User folder does not exist" }

- 400 / 500
{ "error": "<error details>" }

---

## 👥 `/viewallusers` – View All Registered Users

**Method:** GET

Response:
- 200 OK
{ "users": ["user1", "user2", "user3"] }

- 500 Internal Server Error
{ "error": "<error details>" }

---

## 🔍 `/query` – Ask Questions From Uploaded Excel Files

**Method:** POST  
**Content-Type:** application/json

JSON Body:
{
  "query": "What is the revenue in Q1?",
  "userid": "user1"
}

Response:
- 200 OK
{ "response": "The revenue in Q1 is $15,000." }

- 404 Not Found
{ "error": "No vector store found for user user1" }

- 400 / 500
{ "error": "<error details>" }

---

## 🎥 `/video` – Get Video Name and Detail Related to Query

**Method:** POST  
**Content-Type:** application/json

JSON Body:
{
  "query": "Show me the inventory analysis video",
  "userid": "user1"
}

Response:
- 200 OK
{
  "response": {
    "video-name": "inventory-overview.mp4",
    "video-detail": "This video provides an overview of product inventory trends for Q1."
  }
}

- 400 / 404 / 500
{ "error": "<error details>" }

---
