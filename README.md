# TaskMaster - Modern Django Task Management Application 🚀

A feature-rich, modern task management application built with Django. Organize your life with style!

## ✨ Features

### Core Functionality
- ✅ **Create, Read, Update, Delete (CRUD)** tasks
- 🔐 **User Authentication** - Secure login and registration
- 👤 **User-specific Tasks** - Each user sees only their own tasks
- 📊 **Interactive Dashboard** - Visualize your productivity with statistics

### Advanced Features
- 🔍 **Smart Search** - Search tasks by title, description, or tags
- 🎯 **Multi-level Filtering** - Filter by status, priority, and category
- 📈 **Task Sorting** - Sort by due date, priority, creation date, or alphabetically
- 🏷️ **Tags System** - Add custom tags to organize tasks
- ⚡ **AJAX Toggle** - Mark tasks complete without page reload
- 🎨 **Priority Levels** - High, Medium, Low priority badges
- 📅 **Due Date Tracking** - Visual indicators for overdue tasks
- 📊 **Analytics Dashboard** - Track completion rate, overdue tasks, and more

### Task Properties
- **Title** - Short, descriptive task name
- **Description** - Detailed task information
- **Status** - To Do, In Progress, Completed
- **Priority** - High, Medium, Low
- **Category** - Work, Personal, Shopping, Health, Education, Other
- **Tags** - Custom comma-separated tags
- **Due Date** - Optional deadline
- **Timestamps** - Created and updated dates

## 🎨 Modern UI/UX
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🌈 **Beautiful Gradient Backgrounds**
- 💳 **Card-based Layout** - Clean and organized task cards
- 🎯 **Visual Status Indicators** - Color-coded badges for priority and status
- 🔔 **Toast Notifications** - Success/error messages with auto-hide
- ⚠️ **Overdue Highlighting** - Red borders for overdue tasks
- ✓ **Completion Strikethrough** - Visual feedback for completed tasks

## 🛠️ Technology Stack
- **Backend**: Django 5.2.1
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with CSS Variables
- **Icons**: Emoji-based (no external dependencies)

## 📦 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd projects
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create a superuser (optional)**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

7. **Visit** `http://127.0.0.1:8000/`

## 🚀 Usage

### User Pages
- **Home (`/`)** - Landing page with login/signup options
- **Dashboard (`/dashboard/`)** - Analytics and statistics
- **My Tasks (`/userpage/`)** - View, filter, and search tasks
- **Create Task (`/create_task/`)** - Add new tasks
- **Task Details (`/task_details/<id>`)** - View full task information
- **Edit Task (`/edit_task/<id>`)** - Update task details

## 📊 Dashboard Metrics
- **Total Tasks**, **Completed Tasks**, **Pending Tasks**, **Overdue Tasks**
- **Completion Rate** - Percentage progress bar
- **Priority Breakdown** - Tasks by priority level
- **Category Distribution** - Tasks by category
- **Recent & Upcoming Tasks**

## 🎯 Key Improvements Made

1. ✅ **Enhanced Task Model** - Added title, priority, status, tags, and timestamps
2. ✅ **Fixed Forms** - Corrected typo from 'feilds' to 'fields', added validation
3. ✅ **Search & Filter** - Comprehensive search and multi-filter system
4. ✅ **Dashboard** - Statistics, analytics, and productivity metrics
5. ✅ **AJAX Toggle** - Complete tasks without page reload
6. ✅ **Modern CSS** - Card layouts, badges, animations, gradients
7. ✅ **Sorting Options** - Sort by date, priority, title
8. ✅ **Better Templates** - Responsive, card-based, visual indicators
9. ✅ **Toast Notifications** - Auto-hiding success/error messages
10. ✅ **Enhanced Admin** - Better list display, filters, and fieldsets

---

**Happy Task Managing! 📝✨**