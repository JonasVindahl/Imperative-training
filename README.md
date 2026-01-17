# C Programming Practice System

Interactive web-based platform for learning C programming with **620 questions** across 11 categories.

## 🚀 Quick Start

### Local Development
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Access at: `http://localhost:8000`

### TrueNAS SCALE 24.10 Deployment

**Quick Deploy (3 commands):**
```bash
# 1. Copy to TrueNAS
scp -r . root@TRUENAS_IP:/mnt/MainPool/Apps/c-practice

# 2. SSH and deploy
ssh root@TRUENAS_IP
cd /mnt/MainPool/Apps/c-practice && ./deployment/DEPLOY_TRUENAS_SIMPLE.sh

# 3. Access at http://TRUENAS_IP:8000
```

**See full guide:** [README_TRUENAS.md](README_TRUENAS.md)

---

## 📚 Features

- ✅ **620 questions** across 11 categories
- ✅ **5 question types**: Multiple choice, Fill-in-the-blanks, Drag-and-drop, Recursive trace
- ✅ **Bilingual**: English + Danish (faglige begreber)
- ✅ **Safe C compilation**: Sandboxed GCC execution
- ✅ **Progress tracking**: User accounts, adaptive learning
- ✅ **Interactive**: Drag-drop code assembly, step-by-step recursion traces

### Question Categories

| Category | Questions | Topics |
|----------|-----------|--------|
| Memory Management | 65 | malloc, free, calloc, realloc, leaks, dangling pointers |
| Pointers | 65 | Dereferencing, arithmetic, function pointers, void*, const |
| Strings | 70 | strlen, strcpy, strcat, strcmp, strtok, sprintf, safety |
| Structs | 65 | Padding, bit fields, flexible arrays, anonymous, alignment |
| Integer Division | 65 | Bitwise operators, shifts, bit manipulation, two's complement |
| Recursion | 65 | Tree traversal, backtracking, memoization, tail recursion |
| Control Flow | 65 | Loops, switch, goto, short-circuit, Duff's device |
| File I/O | 40 | fopen modes, fread/fwrite, fseek/ftell, buffering |
| Fill-in-the-Blanks | 40 | Professional terminology (EN/DA) |
| Drag-and-Drop | 40 | Code assembly exercises |
| Recursive Trace | 40 | Function call tracing |

---

## 📁 Project Structure

```
7_imperative_exam/
├── app.py                  # Main Flask application
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
│
├── models/                # Database models
│   └── __init__.py        # User, Attempt, Progress
│
├── routes/                # Flask blueprints
│   ├── auth.py           # Authentication
│   ├── practice.py       # Practice sessions
│   └── progress.py       # Dashboard & stats
│
├── services/              # Business logic
│   ├── compiler.py       # Safe C compilation
│   ├── grader.py         # Answer grading (all 5 types)
│   ├── adaptive.py       # Adaptive learning
│   └── question_loader.py # Question management
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── practice.html     # Supports all question types
│   ├── dashboard.html
│   └── ...
│
├── static/               # CSS, images
│   └── css/style.css    # Includes drag-drop, fill-blanks styling
│
├── questions/            # Question bank (620 questions)
│   ├── memory_management.json (65 questions)
│   ├── pointers.json (65 questions)
│   ├── strings.json (70 questions)
│   ├── structs.json (65 questions)
│   ├── integer_division.json (65 questions)
│   ├── recursion.json (65 questions)
│   ├── control_flow.json (65 questions)
│   ├── file_io.json (40 questions)
│   ├── fill_blanks.json (40 questions - EN/DA)
│   ├── drag_drop.json (40 questions)
│   └── recursive_trace.json (40 questions)
│
├── deployment/           # Deployment files
│   ├── DEPLOY_TRUENAS_SIMPLE.sh
│   ├── docker-compose.yml
│   ├── truenas-scale-app.yaml
│   └── deploy.sh
│
├── docs/                 # Documentation
│   ├── NEW_FEATURES.md
│   ├── QUESTION_EXPANSION_REPORT.md
│   ├── TEST_REPORT.md
│   ├── TRUENAS_DEPLOYMENT.md
│   ├── TRUENAS_SCALE_APPS_DEPLOY.md
│   ├── TRUENAS_SCALE_YAML_DEPLOY.md
│   └── QUICKSTART_TRUENAS.md
│
└── README_TRUENAS.md     # TrueNAS quick start guide
```

---

## 🛠️ Technology Stack

**Backend:**
- Python 3.11
- Flask (web framework)
- SQLAlchemy (ORM)
- SQLite (database)
- GCC (C compiler)

**Frontend:**
- HTML5, CSS3, JavaScript
- jQuery, jQuery UI (drag-and-drop)
- Jinja2 templates

**Deployment:**
- Docker / Docker Compose
- TrueNAS SCALE compatible

---

## 📖 Documentation

### Getting Started
- [README_TRUENAS.md](README_TRUENAS.md) - **TrueNAS SCALE quick start** ⭐
- [docs/QUICKSTART_TRUENAS.md](docs/QUICKSTART_TRUENAS.md) - 5-minute deployment

### Deployment Guides
- [docs/TRUENAS_SCALE_YAML_DEPLOY.md](docs/TRUENAS_SCALE_YAML_DEPLOY.md) - YAML deployment (recommended)
- [docs/TRUENAS_SCALE_APPS_DEPLOY.md](docs/TRUENAS_SCALE_APPS_DEPLOY.md) - GUI deployment
- [docs/TRUENAS_DEPLOYMENT.md](docs/TRUENAS_DEPLOYMENT.md) - All deployment methods

### Features & Testing
- [docs/NEW_FEATURES.md](docs/NEW_FEATURES.md) - Feature overview
- [docs/QUESTION_EXPANSION_REPORT.md](docs/QUESTION_EXPANSION_REPORT.md) - Question bank details (224 questions)
- [docs/TEST_REPORT.md](docs/TEST_REPORT.md) - Testing documentation

### Deployment Scripts
- [deployment/DEPLOY_TRUENAS_SIMPLE.sh](deployment/DEPLOY_TRUENAS_SIMPLE.sh) - Auto-deployment
- [deployment/docker-compose.yml](deployment/docker-compose.yml) - Docker Compose
- [deployment/truenas-scale-app.yaml](deployment/truenas-scale-app.yaml) - TrueNAS SCALE YAML

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///instance/practice.db
MAX_CODE_EXECUTION_TIME=3
MAX_MEMORY_MB=50
```

Generate secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database

Automatic initialization on first run. Creates:
- Users table (authentication)
- Progress table (category stats)
- Attempts table (question history)

---

## 🎓 Usage

### For Students

1. **Register** at `/auth/register`
2. **Login** at `/auth/login`
3. **Select category** from dashboard
4. **Practice** with 5 question types:
   - Multiple choice
   - Fill-in-the-blanks (dropdown menus)
   - Drag-and-drop code assembly
   - Recursive function tracing
   - Standard practice questions
5. **Track progress** on dashboard

### For Instructors

- **View progress**: Access SQLite database at `instance/practice.db`
- **Add questions**: Edit JSON files in `questions/` directory
- **Customize**: Modify templates in `templates/` directory

---

## 📊 Statistics

- **Total Questions**: 620
- **Question Types**: 5
- **Categories**: 11
- **Languages**: English + Danish
- **Difficulty Levels**: Easy, Medium, Hard

### Question Distribution

- Multiple Choice: 500 (80.6%)
- Fill-in-the-Blanks: 40 (6.5%)
- Drag-and-Drop: 40 (6.5%)
- Recursive Trace: 40 (6.5%)

---

## 🚀 Deployment Options

### 1. TrueNAS SCALE 24.10 (Recommended)
```bash
./deployment/DEPLOY_TRUENAS_SIMPLE.sh
```
See: [README_TRUENAS.md](README_TRUENAS.md)

### 2. Docker Compose
```bash
cd deployment
docker-compose up -d
```

### 3. Local Development
```bash
pip install -r requirements.txt
python app.py
```

### 4. Production Server
Use Gunicorn + NGINX:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 📝 Adding Questions

Edit JSON files in `questions/` directory. See [docs/QUESTION_EXPANSION_REPORT.md](docs/QUESTION_EXPANSION_REPORT.md) for format details.

Restart app to reload questions.

---

## 🐛 Troubleshooting

### Port Already in Use
Change port in `.env` or `config.py`

### Database Issues
```bash
rm instance/practice.db
python app.py  # Creates fresh database
```

### GCC Not Found
Install GCC:
- macOS: `xcode-select --install`
- Linux: `sudo apt install gcc build-essential`
- Docker: Already included

---

## 🎉 Quick Links

- **Deploy to TrueNAS**: [README_TRUENAS.md](README_TRUENAS.md) ⭐
- **Features Overview**: [docs/NEW_FEATURES.md](docs/NEW_FEATURES.md)
- **Question Bank**: [docs/QUESTION_EXPANSION_REPORT.md](docs/QUESTION_EXPANSION_REPORT.md)
- **All Deployment Methods**: [docs/TRUENAS_DEPLOYMENT.md](docs/TRUENAS_DEPLOYMENT.md)

---

**Status**: ✅ Production Ready | **Questions**: 620 | **Version**: 3.0

Built with ❤️ for C programming education
