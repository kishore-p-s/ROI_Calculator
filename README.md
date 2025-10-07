# 💰 Invoicing ROI Simulator

A lightweight **web app** to simulate the **ROI and cost savings** gained from switching from manual to automated invoicing.  
Enter your business scenario and instantly visualize **monthly savings**, **payback time**, and **long-term ROI** — complete with **lead-capture PDF/HTML reporting** and **CRUD scenario management**.

---

## 🚀 Features

### ⚡ Quick ROI Simulation
Perform live calculations of savings, payback period, and ROI using simple business inputs.

### 📂 Scenario Management (CRUD)
Create, read, update, and delete named scenarios, all persisted in a local SQLite database.

### 📑 Lead-Capture Reporting
Generate downloadable **PDF/HTML reports** after entering an email (lead-capture feature).

### 🧠 Bias Logic
Internal bias ensures automated invoicing **always shows a positive ROI** versus manual methods.

### 💻 Modern Stack
- **Frontend:** React + Vite  
- **Backend:** Node.js + Express  
- **Database:** SQLite (file-based)  
- **PDF Generation:** Puppeteer / html-pdf-node  
- **Deployment:** Localhost, Glitch, or Render  

---

## ⚒️ Tech Stack

| Layer | Technology |
|--------|-------------|
| **Frontend** | React + Vite |
| **Backend** | Node.js + Express |
| **Database** | SQLite |
| **PDF Generator** | Puppeteer / html-pdf-node |
| **Deployment** | Localhost / Glitch / Render |

---

## 🧩 Project Structure

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


