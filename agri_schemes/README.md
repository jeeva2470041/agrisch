# agri_schemes

A new Flutter project.

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.

---

## Backend configuration

The backend uses environment variables. Do NOT commit secrets.

- Copy `backend/.env.example` to `backend/.env` and fill values (e.g. `MONGO_URI`).
- `backend/.env` is ignored by git (added to repository `.gitignore`).
- If you accidentally committed credentials, rotate them immediately and remove the file from history.

# 1. Navigate to backend folder
cd backend

# 2. Create a virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up your .env file (see above)

# 6. Seed the database with scheme data
python seed_db.py

# 7. Run the Flask server
python app.py

