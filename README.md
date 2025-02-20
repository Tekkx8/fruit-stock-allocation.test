# Fruit Stock Allocation System

## Overview
A web application for managing fruit stock and allocating it to customer orders based on restrictions (quality, origin, variety, GGN, supplier) using FIFO logic.

## Architecture
- **Frontend**: React (Bootstrap, React Query, Hooks)
- **Backend**: Flask (Pandas, OpenPyxl, Flask-SQLAlchemy)
- **Database**: SQLite for customer restrictions
- **Storage**: Temporary files (planned migration to cloud)

## Setup
1. **Backend**:
   - `cd backend`
   - `pip install -r requirements.txt`
   - `python app.py`
2. **Frontend**:
   - `cd frontend`
   - `npm install`
   - `npm start`

## API Endpoints
- `/upload_stock` (POST): Upload stock Excel
- `/upload_orders` (POST): Upload orders Excel
- `/allocate_stock` (POST): Allocate stock
- `/get_restrictions` (GET): Get customer restrictions

## Deployment
- Backend on Render, Frontend on Netlify. Use `.env` for API URLs.

## Contributing
Add tests, optimize performance, and enhance UI.
