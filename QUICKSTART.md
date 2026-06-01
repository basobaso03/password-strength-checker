# Quick Start Guide - Password Strength Checker 🚀

## 5-Minute Setup

### Prerequisites
- Python 3.8 or higher
- Modern web browser

### Step 1: Prepare Environment (1 min)
```bash
cd password-strength-checker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies (1 min)
```bash
pip install -r backend/requirements.txt
```

### Step 3: Run Tests (1 min, Optional)
```bash
pytest backend/tests/ -v --tb=short
```

### Step 4: Start Backend (1 min)
```bash
python backend/app.py
```

**Expected Output:**
```
 * Running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

### Step 5: Open Frontend (1 min)
1. Open the root `index.html` file directly in your browser.
2. Start typing a password!
3. See instant real-time analysis (Note: if the backend server is not running, the application will automatically fall back to client-side analysis in the browser).

---

## Quick Testing

### Test with cURL
```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"password": "TestPassword123!"}'
```

### Test Health Check
```bash
curl http://localhost:5000/api/health
```

---

## Troubleshooting

### Issue: "Module not found" error
**Solution:**
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Then install requirements again
pip install -r backend/requirements.txt
```

### Issue: Port 5000 already in use
**Solution:**
```bash
# Change port in app.py line ~95:
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001

# Update frontend/script.js line ~5:
const API_BASE_URL = 'http://localhost:5001/api';  # Change port here too
```

### Issue: CORS errors in browser console
**Solution:** Make sure the Flask backend is running:
```bash
python backend/app.py
```

### Issue: "Cannot find module 'pytest'" when running tests
**Solution:**
```bash
pip install pytest pytest-cov
pytest backend/tests/ -v
```

---

## Common Tasks

### Run All Tests with Coverage
```bash
pytest backend/tests/ --cov=backend --cov-report=html
open htmlcov/index.html  # or start > htmlcov/index.html on Windows
```

### Run Specific Test
```bash
pytest backend/tests/test_checker.py::TestPasswordStrengthChecker::test_strong_password_classification -v
```

### Check Test Coverage Report
```bash
pytest backend/tests/ --cov=backend --cov-report=term-missing
```

### Run Frontend with Simple Server
```bash
python -m http.server 8000
# Open http://localhost:8000 in browser
```

---

## Project Structure Quick Reference

```
password-strength-checker/
├── backend/
│   ├── app.py          ← Start here! (flask app)
│   ├── checker.py      ← Core password logic
│   ├── requirements.txt ← Dependencies
│   └── tests/          ← Run: pytest backend/tests/ -v
├── docs/
│   ├── ARCHITECTURE.md ← System design
│   └── API.md          ← Endpoint docs
├── index.html          ← Open in browser! (GitHub Pages root)
├── styles.css          ← Beautiful styling
├── script.js           ← Frontend logic and client-side analyzer fallback
├── README.md           ← Full documentation
├── LEARNING.md         ← Skills learned
└── .gitignore          ← Git configuration
```

---

## Next Steps

1. ✅ Follow 5-minute setup above
2. 📖 Read [README.md](README.md) for full documentation
3. 🏗️ Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
4. 📚 Read [LEARNING.md](LEARNING.md) for skills learned
5. 🧪 Run tests: `pytest backend/tests/ -v`
6. 💡 Explore the code and try making changes!

---

## Example Passwords to Test

**Weak Passwords** 🔴
```
password
123456
admin
abc123
```

**Medium Passwords** 🟡
```
Password123
Admin@1234
MyPassword1
TestPass@2024
```

**Strong Passwords** 🟢
```
Str0ng!@#$Passw0rd
P@ssw0rd123!xyzABC
MySecurePass@2024!
```

---

## API Endpoints Cheat Sheet

```bash
# Check password strength
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"password": "MyPassword123!"}'

# Health check
curl http://localhost:5000/api/health

# Get API info
curl http://localhost:5000/api/info
```

---

## Key Features

✅ Real-time password analysis  
✅ Beautiful responsive UI  
✅ REST API backend  
✅ 80+ unit tests  
✅ Comprehensive documentation  
✅ Production-ready code  
✅ Security best practices  
✅ Easy to extend and modify  

---

## Support

📧 **Email**: baseramarlvin@gmail.com  
💼 **LinkedIn**: https://www.linkedin.com/in/marlvin-basera-359939286  

---

**Happy Learning! 🎓**

For detailed information, see [README.md](README.md)
