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
├── backend/ # Express + Node.js API
│ ├── config/ # MongoDB connection setup
│ ├── models/ # Mongoose schemas (Scenario)
│ ├── routes/ # API routes (simulate, scenarios, reports)
│ ├── controllers/ # Business logic & calculations
│ ├── utils/ # Helper functions and constants
│ ├── server.js # Express server entry point
│ ├── package.json
│ └── .env.example # Environment variables
│
├── frontend/ # React frontend
│ ├── src/
│ │ ├── components/ # UI Components (Form, Chart, Report)
│ │ ├── pages/ # Main views (Simulator, Saved Scenarios)
│ │ ├── services/ # Axios calls to backend API
│ │ ├── styles/ # CSS/Tailwind styling
│ │ └── main.jsx # App entry point
│ ├── public/
│ ├── vite.config.js
│ └── package.json
│
├── README.md
└── .gitignore
```


## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/invoicing-roi-simulator.git
cd invoicing-roi-simulator
```

2️⃣ Backend Setup
bash
Copy code
cd backend
npm install
cp .env.example .env
# Add your MongoDB connection string in .env
npm start
Backend will run at: http://localhost:5000

3️⃣ Frontend Setup
bash
Copy code
cd ../frontend
npm install
npm run dev
Frontend will run at: http://localhost:5173

📡 API Endpoints
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
```
json
Copy code
{
  "monthly_savings": 8200,
  "payback_months": 6.2,
  "roi_percentage": 410,
  "net_savings": 245000
}
```

🧮 Calculation Logic
1. Manual Labor Cost
```
Copy code
labor_cost_manual = num_ap_staff × hourly_wage × avg_hours_per_invoice × monthly_invoice_volume
```
2. Automation Cost
```
Copy code
auto_cost = monthly_invoice_volume × automated_cost_per_invoice
```

3. Error Savings
```
Copy code
error_savings = (error_rate_manual − error_rate_auto) × monthly_invoice_volume × error_cost
```
4. Monthly Savings (with bias)
```
Copy code
monthly_savings = ((labor_cost_manual + error_savings) − auto_cost) × min_roi_boost_factor
```
5. Cumulative ROI
```
Copy code
cumulative_savings = monthly_savings × time_horizon_months
net_savings = cumulative_savings − one_time_implementation_cost
payback_months = one_time_implementation_cost ÷ monthly_savings
roi_percentage = (net_savings ÷ one_time_implementation_cost) × 100
```

🧾 Example Simulation
| Input                 | Value |
| --------------------- | ----- |
| Invoices per month    | 2000  |
| Staff                 | 3     |
| Avg hours per invoice | 0.17  |
| Hourly wage           | $30   |
| Error cost            | $100  |

Output:

Monthly savings: $8,200
Payback period: 6.2 months
ROI (36 months): ~400%

👨‍💻 Author
Kishore P.S.
Built as part of a 3-hour product challenge.
