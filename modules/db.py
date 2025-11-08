import sqlite3
import hashlib

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('learning_app.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the necessary tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT NOT NULL,
            level TEXT,
            topic_index INTEGER DEFAULT 0,
            status TEXT DEFAULT 'learning',
            assignment_score INTEGER,
            study_hours_per_day REAL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def add_user_to_db(username, hashed_password):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, hashed_password) VALUES (?, ?)',
            (username, hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_from_db(username):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    return user

def get_or_create_progress(user_id, subject):
    conn = get_db_connection()
    progress = conn.execute(
        'SELECT * FROM progress WHERE user_id = ? AND subject = ?',
        (user_id, subject)
    ).fetchone()
    
    if not progress:
        conn.execute(
            'INSERT INTO progress (user_id, subject) VALUES (?, ?)',
            (user_id, subject)
        )
        conn.commit()
        progress = conn.execute(
            'SELECT * FROM progress WHERE user_id = ? AND subject = ?',
            (user_id, subject)
        ).fetchone()

    conn.close()
    return progress

def update_progress(user_id, subject, level=None, topic_index=None, status=None, score=None):
    conn = get_db_connection()
    if level is not None:
        conn.execute('UPDATE progress SET level = ? WHERE user_id = ? AND subject = ?', (level, user_id, subject))
    if topic_index is not None:
        conn.execute('UPDATE progress SET topic_index = ? WHERE user_id = ? AND subject = ?', (topic_index, user_id, subject))
    if status is not None:
        conn.execute('UPDATE progress SET status = ? WHERE user_id = ? AND subject = ?', (status, user_id, subject))
    if score is not None:
        conn.execute('UPDATE progress SET assignment_score = ? WHERE user_id = ? AND subject = ?', (score, user_id, subject))
    conn.commit()
    conn.close()

def get_all_user_progress(user_id):
    """Fetches all progress records for a given user."""
    conn = get_db_connection()
    progress_records = conn.execute(
        'SELECT * FROM progress WHERE user_id = ?', (user_id,)
    ).fetchall()
    conn.close()
    return progress_records

def update_study_hours(user_id, subject, hours_per_day):
    """Updates the study hours per day for a user's subject."""
    conn = get_db_connection()
    conn.execute(
        'UPDATE progress SET study_hours_per_day = ? WHERE user_id = ? AND subject = ?',
        (hours_per_day, user_id, subject)
    )
    conn.commit()
    conn.close()

def get_study_hours(user_id, subject):
    """Gets the study hours per day for a user's subject."""
    conn = get_db_connection()
    result = conn.execute(
        'SELECT study_hours_per_day FROM progress WHERE user_id = ? AND subject = ?',
        (user_id, subject)
    ).fetchone()
    conn.close()
    return result['study_hours_per_day'] if result and result['study_hours_per_day'] else None

def get_todays_study_plan(user_id, subject):
    """
    Calculates what the user should study TODAY based on their study plan.
    Returns the topics scheduled for today.
    """
    import json
    from datetime import datetime, timedelta
    
    # Get user's progress and study hours
    conn = get_db_connection()
    progress = conn.execute(
        'SELECT * FROM progress WHERE user_id = ? AND subject = ?',
        (user_id, subject)
    ).fetchone()
    conn.close()
    
    if not progress or not progress['study_hours_per_day']:
        return None 
    
    saved_hours = progress['study_hours_per_day']
    current_topic_index = progress['topic_index']
    user_level = progress['level']
    

    try:
        with open(f"curriculum/{subject.lower()}_curriculum.json") as f:
            curriculum = json.load(f)['full_path']
    except FileNotFoundError:
        return None
    
    total_topics = len(curriculum)
    
    daily_schedule = []
    current_day = 1
    hours_accumulated = 0
    topics_for_today = []
    
    for i in range(current_topic_index, total_topics):
        topic_name = curriculum[i]['topic']
        topic_level = curriculum[i]['level']
        topic_index = i
        
        if user_level == 'beginner':
            if topic_level == 'beginner':
                topic_hours = 1.0
            elif topic_level == 'intermediate':
                topic_hours = 1.5
            else:  
                topic_hours = 2.0
        elif user_level == 'intermediate':
            if topic_level == 'beginner':
                topic_hours = 0.5
            elif topic_level == 'intermediate':
                topic_hours = 1.0
            else:  
                topic_hours = 1.5
        elif user_level == 'advanced':
            if topic_level == 'beginner':
                topic_hours = 0.3
            elif topic_level == 'intermediate':
                topic_hours = 0.5
            else:  
                topic_hours = 1.0
        else:
            topic_hours = 1.0
        
        # Check if this topic fits in today's schedule
        if hours_accumulated + topic_hours <= saved_hours:
            topics_for_today.append({
                'topic': topic_name,
                'level': topic_level,
                'hours': topic_hours,
                'index': topic_index
            })
            hours_accumulated += topic_hours
        else:
            if topics_for_today:
                daily_schedule.append({
                    'day': current_day,
                    'topics': topics_for_today.copy(),
                    'total_hours': hours_accumulated
                })
            
            current_day += 1
            topics_for_today = [{
                'topic': topic_name,
                'level': topic_level,
                'hours': topic_hours,
                'index': topic_index
            }]
            hours_accumulated = topic_hours
    
    # Don't forget the last day!
    if topics_for_today:
        daily_schedule.append({
            'day': current_day,
            'topics': topics_for_today.copy(),
            'total_hours': hours_accumulated
        })
    
   # Calculate which day user is actually on
    if not daily_schedule:
        return None
    
    
    user_current_day = 1  
    
    # If user has progressed beyond the first topic of the plan
    if current_topic_index > progress['topic_index']:
        user_current_day = 1
    
    return {
        'day': user_current_day,
        'topics': daily_schedule[0]['topics'],  # First day of remaining schedule
        'total_hours': daily_schedule[0]['total_hours'],
        'total_days': len(daily_schedule),
        'completed_topics': current_topic_index  # Track how many completed
    }