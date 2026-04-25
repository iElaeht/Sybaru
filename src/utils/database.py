import sqlite3
import os
import psycopg2
from psycopg2 import extras

# --- CONFIGURACIÓN DE RUTAS Y CONEXIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "sybaru_data.db")
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Retorna una conexión a PostgreSQL (Railway) o SQLite (Local)."""
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        return sqlite3.connect(DB_PATH)

def get_placeholder():
    """Retorna el marcador de posición correcto: %s para Postgres, ? para SQLite."""
    return "%s" if DATABASE_URL else "?"

def init_db():
    """Inicializa la base de datos con todas las tablas necesarias."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Playlists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_playlists (
            user_id VARCHAR(50),
            song_title TEXT,
            song_url TEXT,
            PRIMARY KEY (user_id, song_url)
        )
    ''')
    
    # 2. Prefijos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guild_prefixes (
            guild_id VARCHAR(50) PRIMARY KEY,
            prefix VARCHAR(10) NOT NULL
        )
    ''')

    # 3. Crosshairs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_crosshairs (
            user_id VARCHAR(50),
            title VARCHAR(100), 
            code TEXT,
            PRIMARY KEY (user_id, title)
        )
    ''')

    # 4. Sensibilidades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sensitivities (
            user_id VARCHAR(50),
            title VARCHAR(100), 
            dpi VARCHAR(20),
            sens_in_game VARCHAR(20),
            scoped_mult VARCHAR(20) DEFAULT '1.0',
            ads_mult VARCHAR(20) DEFAULT '1.0',
            PRIMARY KEY (user_id, title)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print(f"🗄️ DB Sincronizada en {'MODO NUBE (Postgres)' if DATABASE_URL else 'MODO LOCAL (SQLite)'}")

# --- MÓDULO DE PREFIJOS ---
def set_guild_prefix(guild_id, prefix):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if DATABASE_URL:
                    cursor.execute(f"INSERT INTO guild_prefixes (guild_id, prefix) VALUES ({p}, {p}) ON CONFLICT (guild_id) DO UPDATE SET prefix = EXCLUDED.prefix", (str(guild_id), prefix))
                else:
                    cursor.execute(f"INSERT OR REPLACE INTO guild_prefixes (guild_id, prefix) VALUES ({p}, {p})", (str(guild_id), prefix))
                conn.commit()
        return True
    except Exception: return False

def get_guild_prefix(guild_id, default):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT prefix FROM guild_prefixes WHERE guild_id = {p}", (str(guild_id),))
                result = cursor.fetchone()
                return result[0] if result else default
    except Exception: return default

def reset_guild_prefix(guild_id):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM guild_prefixes WHERE guild_id = {p}", (str(guild_id),))
                conn.commit()
        return True
    except Exception: return False

# --- MÓDULO DE PLAYLISTS ---
def save_to_playlist(user_id, title, url):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"INSERT INTO user_playlists (user_id, song_title, song_url) VALUES ({p}, {p}, {p})", (str(user_id), title, url))
                conn.commit()
        return True
    except Exception: return False

def get_playlist(user_id):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT song_title, song_url FROM user_playlists WHERE user_id = {p}", (str(user_id),))
                return cursor.fetchall()
    except Exception: return []

def delete_from_playlist(user_id, song_url):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM user_playlists WHERE user_id = {p} AND song_url = {p}", (str(user_id), song_url))
                conn.commit()
        return True
    except Exception: return False

def clear_full_playlist(user_id):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM user_playlists WHERE user_id = {p}", (str(user_id),))
                conn.commit()
        return True
    except Exception: return False

# --- MÓDULO DE CROSSHAIRS ---
def add_crosshair(user_id, title, code):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"INSERT INTO user_crosshairs (user_id, title, code) VALUES ({p}, {p}, {p})", (str(user_id), title, code))
                conn.commit()
        return True
    except Exception: return False

def get_crosshairs(user_id):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT title, code FROM user_crosshairs WHERE user_id = {p}", (str(user_id),))
                return cursor.fetchall()
    except Exception: return []

def update_crosshair(user_id, title, new_code):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"UPDATE user_crosshairs SET code = {p} WHERE user_id = {p} AND title = {p}", (new_code, str(user_id), title))
                conn.commit()
        return True
    except Exception: return False

def delete_crosshair(user_id, title):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM user_crosshairs WHERE user_id = {p} AND title = {p}", (str(user_id), title))
                conn.commit()
        return True
    except Exception: return False

# --- MÓDULO DE SENSIBILIDADES ---
def add_sensitivity(user_id, title, dpi, sens, scoped, ads):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"INSERT INTO user_sensitivities (user_id, title, dpi, sens_in_game, scoped_mult, ads_mult) VALUES ({p}, {p}, {p}, {p}, {p}, {p})", 
                               (str(user_id), title, dpi, sens, scoped, ads))
                conn.commit()
        return True
    except Exception: return False

def get_sensitivities(user_id):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT title, dpi, sens_in_game, scoped_mult, ads_mult FROM user_sensitivities WHERE user_id = {p}", (str(user_id),))
                return cursor.fetchall()
    except Exception: return []

def update_sensitivity(user_id, title, dpi, sens, scoped, ads):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE user_sensitivities 
                    SET dpi = {p}, sens_in_game = {p}, scoped_mult = {p}, ads_mult = {p} 
                    WHERE user_id = {p} AND title = {p}
                """, (dpi, sens, scoped, ads, str(user_id), title))
                conn.commit()
        return True
    except Exception: return False

def delete_sensitivity(user_id, title):
    p = get_placeholder()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM user_sensitivities WHERE user_id = {p} AND title = {p}", (str(user_id), title))
                conn.commit()
        return True
    except Exception: return False

remove_from_playlist = delete_from_playlist