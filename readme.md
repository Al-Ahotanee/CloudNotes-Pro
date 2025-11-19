# ☁️ CloudNotes Pro

**Enterprise-grade Academic Notes Sharing Platform built with Flask, Tailwind CSS, and SQLite**

A production-ready, full-stack web application for universities and educational institutions to facilitate note sharing among students and faculty.

---

## 🚀 Features

### Core Functionality
- **🔐 Secure Authentication System** - User registration, login, and session management
- **📤 File Upload & Storage** - Real file storage with support for multiple formats (PDF, DOC, PPT, etc.)
- **🔍 Advanced Search & Filtering** - Search by title, category, subject, tags with sorting options
- **⭐ Rating & Review System** - Community-driven quality assessment
- **📊 User Profiles & Statistics** - Track uploads, downloads, and contributions
- **🗑️ Content Management** - Users can delete their own notes, admins have full control

### Technical Highlights
- **RESTful API Architecture** - Clean, well-documented endpoints
- **SQLite Database** - Lightweight, embedded database with full ACID compliance
- **Responsive Design** - Mobile-first UI with Tailwind CSS
- **Production-Ready** - Error handling, security features, and optimized for deployment
- **Cloud-Deployable** - Configured for Render, Heroku, and other cloud platforms

---

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for version control)

---

## 🛠️ Local Installation & Setup

### 1. Clone or Create Project

```bash
# Create project directory
mkdir cloudnotes-pro
cd cloudnotes-pro
```

### 2. Create Required Files

Create the following directory structure:

```
cloudnotes-pro/
├── app.py
├── requirements.txt
├── Procfile
├── render.yaml
├── .env
├── .gitignore
├── templates/
│   └── index.html
└── uploaded_files/
    └── .gitkeep
```

### 3. Create `.gitkeep` in uploaded_files

```bash
mkdir uploaded_files
touch uploaded_files/.gitkeep
```

### 4. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 5. Set Environment Variables

Create a `.env` file:

```bash
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_APP=app.py
```

### 6. Run the Application

```bash
# Initialize database and start server
python app.py
```

The application will be available at `http://localhost:5000`

---

## 🌐 Deployment to Render

### Method 1: Using GitHub (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/cloudnotes-pro.git
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `cloudnotes-pro`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Add Environment Variable:
     - `SECRET_KEY`: (Generate a random string)
   - Click "Create Web Service"

### Method 2: Using Render Blueprint

The included `render.yaml` file enables one-click deployment:

1. Push your code to GitHub
2. In Render dashboard, click "New +" → "Blueprint"
3. Connect your repository
4. Render will automatically detect `render.yaml` and deploy

### Post-Deployment

1. **Access your app** at the provided Render URL (e.g., `https://cloudnotes-pro.onrender.com`)
2. **Test the demo accounts**:
   - Admin: `admin` / `admin123`
   - Student: `student1` / `pass123`
   - Professor: `professor` / `prof123`

---

## 🎯 Usage Guide

### For Students

1. **Register/Login** - Create an account or use demo credentials
2. **Browse Notes** - Search and filter by category, subject, or keywords
3. **Download** - Click download button on any note card
4. **Upload** - Share your own notes via the Upload tab
5. **Rate** - Provide feedback on notes you've downloaded
6. **Profile** - Track your uploads and downloads

### For Teachers/Admins

All student features plus:
- Delete any notes (admins only)
- Access to all statistics
- Moderation capabilities

---

## 🔒 Security Features

- **Password Hashing** - Uses Werkzeug's secure password hashing
- **Session Management** - Secure cookie-based sessions
- **File Validation** - Whitelist of allowed file extensions
- **Size Limits** - 50MB max file size to prevent abuse
- **SQL Injection Protection** - Parameterized queries throughout
- **CSRF Protection** - Built into Flask
- **Input Sanitization** - Secure filename handling with Werkzeug

---

## 📁 Project Structure

```
cloudnotes-pro/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Procfile               # Process configuration for deployment
├── render.yaml            # Render deployment configuration
├── .env                   # Environment variables (not in Git)
├── .gitignore            # Git ignore patterns
├── templates/
│   └── index.html        # Single-page application UI
├── uploaded_files/       # User-uploaded files storage
└── notes_system.db       # SQLite database (auto-created)
```

---

## 🗄️ Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `password` - Hashed password
- `email` - User email
- `role` - student/teacher/admin
- `created_at` - Registration timestamp

### Notes Table
- `id` - Primary key
- `title` - Note title
- `category` - Subject category
- `subject` - Specific subject
- `description` - Note description
- `uploader_id` - Foreign key to users
- `upload_date` - Upload timestamp
- `downloads` - Download count
- `tags` - JSON array of tags
- `file_path` - Physical file location
- `file_name` - Original filename
- `file_size` - File size in bytes
- `rating_sum` - Sum of all ratings
- `rating_count` - Number of ratings

### Ratings Table
- `id` - Primary key
- `note_id` - Foreign key to notes
- `user_id` - Foreign key to users
- `rating` - 1-5 star rating
- `review` - Optional text review
- `created_at` - Rating timestamp

### Download History Table
- `id` - Primary key
- `note_id` - Foreign key to notes
- `user_id` - Foreign key to users
- `download_date` - Download timestamp

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/status` - Check authentication status

### Notes
- `GET /api/notes/search` - Search notes with filters
- `GET /api/notes/categories` - Get all categories
- `POST /api/notes/upload` - Upload new note
- `GET /api/notes/download/<id>` - Download note file
- `POST /api/notes/rate` - Rate a note
- `DELETE /api/notes/delete/<id>` - Delete a note

### User
- `GET /api/user/profile` - Get user profile and statistics

---

## 🛠️ Customization

### Adding New Categories

Edit the categories list in `templates/index.html`:

```javascript
<option value="Your Category">Your Category</option>
```

### Changing File Size Limit

In `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

### Adding File Types

In `app.py`:

```python
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'zip', 'mp4'}
```

---

## 🐛 Troubleshooting

### Database Issues

```bash
# Delete and recreate database
rm notes_system.db
python app.py
```

### File Upload Errors

- Check `uploaded_files/` directory exists and is writable
- Verify file size is under 50MB
- Ensure file extension is in allowed list

### Deployment Issues on Render

- Verify `Procfile` exists in root directory
- Check environment variables are set
- Review build logs in Render dashboard
- Ensure `gunicorn` is in requirements.txt

---

## 📈 Performance Optimization

### For Production

1. **Enable Caching** - Add Flask-Caching for API responses
2. **Use PostgreSQL** - For better concurrent access (change from SQLite)
3. **CDN for Static Assets** - Host Tailwind CSS locally
4. **Add Redis** - For session storage and caching
5. **Implement Rate Limiting** - Prevent abuse with Flask-Limiter

### Database Optimization

```python
# Add indexes for faster queries
cursor.execute("CREATE INDEX idx_notes_category ON notes(category)")
cursor.execute("CREATE INDEX idx_notes_uploader ON notes(uploader_id)")
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- Flask framework for the robust backend
- Tailwind CSS for beautiful, responsive UI
- SQLite for reliable data storage
- Render for easy deployment

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team
- Check the documentation

---

## 🎓 Demo Accounts

The application comes with pre-configured demo accounts:

| Username  | Password  | Role      |
|-----------|-----------|-----------|
| admin     | admin123  | Admin     |
| student1  | pass123   | Student   |
| professor | prof123   | Teacher   |

---

## ✨ Features Roadmap

- [ ] Email notifications for new uploads
- [ ] Advanced analytics dashboard
- [ ] PDF preview functionality
- [ ] Collaborative note editing
- [ ] Mobile app (React Native)
- [ ] Integration with LMS platforms
- [ ] AI-powered note recommendations
- [ ] Multi-language support

---

**Built with ❤️ for the education community**
