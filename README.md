# 💰 Invoicing ROI Simulator

An interactive web app that calculates the Return on Investment (ROI) of switching from manual to automated invoicing.  
Built using the **MERN stack (MongoDB, Express, React, Node.js)**, it allows users to simulate cost savings, manage scenarios, and generate downloadable reports.

---

## 🧭 Table of Contents
1. [Overview](#-overview)
2. [Features](#-features)
3. [Tech Stack](#-tech-stack)
4. [Project Structure](#-project-structure)
5. [Installation & Setup](#-installation--setup)
6. [API Endpoints](#-api-endpoints)
7. [Calculation Logic](#-calculation-logic)
8. [Example Simulation](#-example-simulation)
9. [Future Enhancements](#-future-enhancements)

---

## 🎯 Overview
The **Invoicing ROI Simulator** helps businesses visualize their savings and payback when moving from manual invoicing to automation.  
It takes user inputs such as invoice volume, staff size, and error rate to calculate monthly savings, ROI, and payback period — using a bias factor that ensures automation always appears advantageous.

---

## 🚀 Features
✅ Real-time ROI and payback simulation  
✅ Scenario management (Save, Retrieve, Delete)  
✅ Email-gated PDF/HTML report generation  
✅ RESTful API with JSON responses  
✅ Persistent storage using MongoDB  
✅ Easy to deploy locally or online (Render, Vercel, etc.)

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-------------|
| Frontend | React + Vite + TailwindCSS |
| Backend | Node.js + Express.js |
| Database | MongoDB (via Mongoose) |
| Report Generation | pdfkit / html-pdf |
| Hosting (Optional) | Render / Vercel / ngrok |

---

## 🧩 Project Structure

```
invoicing-roi-simulator/
│
├── api/ # Express backend
│ ├── db/ # SQLite database and schema
│ ├── routes/ # Express routes (simulate, report, scenarios)
│ ├── handlers/ # Business logic and calculations
│ ├── utils/ # Helper and configuration files
│ ├── package.json # Backend dependencies
│ └── server.js # Express server entry point
│
├── frontend/ # React + Vite frontend
│ ├── src/
│ │ ├── components/ # UI components (Forms, Charts, Reports)
│ │ ├── pages/ # Main pages (Dashboard, Scenarios)
│ │ ├── services/ # API calls to backend
│ │ ├── styles/ # CSS or Tailwind styling
│ │ └── main.jsx # Frontend entry point
│ ├── public/ # Static files
│ ├── vite.config.js # Vite configuration
│ └── package.json # Frontend dependencies
│
├── README.md # Project documentation
└── .gitignore
```


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/invoicing-roi-simulator.git
cd invoicing-roi-simulator
```

###2️⃣ Backend Setup
cd backend
npm install
cp .env.example .env
# Add your MongoDB connection string in .env
npm start
Backend will run at: http://localhost:5000

3️⃣ Frontend Setup
cd ../frontend
npm install
npm run dev
Frontend will run at: http://localhost:5173

| Method     | Endpoint               | Description                                   |
| ---------- | ---------------------- | --------------------------------------------- |
| **POST**   | `/api/simulate`        | Run ROI simulation and return results         |
| **POST**   | `/api/scenarios`       | Save simulation scenario                      |
| **GET**    | `/api/scenarios`       | Retrieve all saved scenarios                  |
| **GET**    | `/api/scenarios/:id`   | Get single scenario details                   |
| **DELETE** | `/api/scenarios/:id`   | Delete a scenario                             |
| **POST**   | `/api/report/generate` | Generate downloadable report (email required) |

All responses return JSON.
Example response for /simulate:
{
  "monthly_savings": 8200,
  "payback_months": 6.2,
  "roi_percentage": 410,
  "net_savings": 245000
}

Calculation Logic

1. Manual Labor Cost
  labor_cost_manual = num_ap_staff × hourly_wage × avg_hours_per_invoice × monthly_invoice_volume
