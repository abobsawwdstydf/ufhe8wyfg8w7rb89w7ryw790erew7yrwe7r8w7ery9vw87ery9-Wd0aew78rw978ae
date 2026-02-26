"""Общий модуль для работы с базой данных Neon"""
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL


def get_connection():
    """Получить соединение с БД"""
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Инициализация таблиц для всех ботов"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Таблица для corporate бота - статистика пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS corporate_users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(255),
            first_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица для link shortener бота
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shortened_links (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            original_url TEXT NOT NULL,
            short_code VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица для support бота - тикеты
    cur.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id SERIAL PRIMARY KEY,
            ticket_id VARCHAR(50) UNIQUE NOT NULL,
            user_id BIGINT NOT NULL,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            message TEXT NOT NULL,
            priority VARCHAR(50),
            status VARCHAR(50) DEFAULT 'Новый',
            note TEXT,
            admin_id BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolution_date TIMESTAMP
        )
    """)
    
    # Таблица для support бота - архив
    cur.execute("""
        CREATE TABLE IF NOT EXISTS support_archive (
            id SERIAL PRIMARY KEY,
            ticket_id VARCHAR(50) UNIQUE NOT NULL,
            user_id BIGINT NOT NULL,
            username VARCHAR(255),
            message TEXT,
            priority VARCHAR(50),
            status VARCHAR(50),
            rating INTEGER,
            created_at TIMESTAMP,
            resolution_date TIMESTAMP
        )
    """)
    
    # Таблица для uid_info бота - статистика запросов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS uid_requests (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            target_username VARCHAR(255),
            target_id BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ База данных инициализирована")


# Функции для corporate бота
def add_corporate_user(user_id, username, first_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO corporate_users (user_id, username, first_name) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
        (user_id, username, first_name)
    )
    conn.commit()
    cur.close()
    conn.close()


# Функции для link shortener бота
def add_shortened_link(user_id, original_url, short_code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO shortened_links (user_id, original_url, short_code) VALUES (%s, %s, %s)",
        (user_id, original_url, short_code)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_user_links_count(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM shortened_links WHERE user_id = %s", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


# Функции для support бота
def create_ticket(ticket_id, user_id, username, first_name, last_name, message, priority):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO support_tickets (ticket_id, user_id, username, first_name, last_name, message, priority)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (ticket_id, user_id, username, first_name, last_name, message, priority))
    conn.commit()
    cur.close()
    conn.close()


def update_ticket_status(ticket_id, status, admin_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if admin_id:
        cur.execute(
            "UPDATE support_tickets SET status = %s, admin_id = %s WHERE ticket_id = %s",
            (status, admin_id, ticket_id)
        )
    else:
        cur.execute(
            "UPDATE support_tickets SET status = %s WHERE ticket_id = %s",
            (status, ticket_id)
        )
    conn.commit()
    cur.close()
    conn.close()


def add_ticket_note(ticket_id, note):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE support_tickets SET note = %s WHERE ticket_id = %s", (note, ticket_id))
    conn.commit()
    cur.close()
    conn.close()


def resolve_ticket(ticket_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO support_archive (ticket_id, user_id, username, message, priority, status, created_at, resolution_date)
        SELECT ticket_id, user_id, username, message, priority, status, created_at, CURRENT_TIMESTAMP
        FROM support_tickets WHERE ticket_id = %s
        ON CONFLICT (ticket_id) DO UPDATE SET status = EXCLUDED.status, resolution_date = EXCLUDED.resolution_date
    """, (ticket_id,))
    cur.execute("DELETE FROM support_tickets WHERE ticket_id = %s", (ticket_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_ticket(ticket_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM support_tickets WHERE ticket_id = %s", (ticket_id,))
    ticket = cur.fetchone()
    cur.close()
    conn.close()
    return ticket


def get_next_ticket_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM support_tickets")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count + 1


def get_all_tickets():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM support_tickets ORDER BY created_at DESC")
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return tickets


def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM support_archive")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


# Функции для uid_info бота
def add_uid_request(user_id, target_username, target_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO uid_requests (user_id, target_username, target_id) VALUES (%s, %s, %s)",
        (user_id, target_username, target_id)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_user_requests_count(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM uid_requests WHERE user_id = %s", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count
