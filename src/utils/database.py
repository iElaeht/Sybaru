import sqlite3
import os

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "sybaru_data.db")

def init_db():
    """Inicializa la base de datos con todas las tablas optimizadas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Tabla de Playlists (Música por usuario)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_playlists (
            user_id TEXT,
            song_title TEXT,
            song_url TEXT,
            PRIMARY KEY (user_id, song_url)
        )
    ''')
    
    # 2. Tabla de Prefijos (Configuración por servidor)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guild_prefixes (
            guild_id TEXT PRIMARY KEY,
            prefix TEXT NOT NULL
        )
    ''')

    # 3. Tabla de Crosshairs (Smart Mode con NOCASE)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_crosshairs (
            user_id TEXT,
            title TEXT COLLATE NOCASE, 
            code TEXT,
            PRIMARY KEY (user_id, title)
        )
    ''')

    # 4. Tabla de Sensibilidades (Actualizada para Scoped y ADS)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sensitivities (
            user_id TEXT,
            title TEXT COLLATE NOCASE, 
            dpi TEXT,
            sens_in_game TEXT,
            scoped_mult TEXT DEFAULT '1.0',
            ads_mult TEXT DEFAULT '1.0',
            PRIMARY KEY (user_id, title)
        )
    ''')
    
    # --- PARCHE DE MIGRACIÓN (Por si la tabla ya existía sin Scoped/ADS) ---
    try:
        cursor.execute("ALTER TABLE user_sensitivities ADD COLUMN scoped_mult TEXT DEFAULT '1.0'")
        cursor.execute("ALTER TABLE user_sensitivities ADD COLUMN ads_mult TEXT DEFAULT '1.0'")
    except sqlite3.OperationalError:
        pass # Las columnas ya existen

    conn.commit()
    conn.close()
    print("🗄️ DB Sincronizada: Soporte para Sens, Scoped y ADS activado.")

# --- MÓDULO DE PREFIJOS ---
def set_guild_prefix(guild_id, prefix):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO guild_prefixes (guild_id, prefix) VALUES (?, ?)", (str(guild_id), prefix))
            conn.commit()
        return True
    except Exception: return False

def get_guild_prefix(guild_id, default):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT prefix FROM guild_prefixes WHERE guild_id = ?", (str(guild_id),))
            result = cursor.fetchone()
            return result[0] if result else default
    except Exception: return default

def reset_guild_prefix(guild_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM guild_prefixes WHERE guild_id = ?", (str(guild_id),))
            conn.commit()
        return True
    except Exception: return False

# --- MÓDULO DE PLAYLISTS ---
def save_to_playlist(user_id, title, url):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_playlists (user_id, song_title, song_url) VALUES (?, ?, ?)", (str(user_id), title, url))
            conn.commit()
        return True
    except sqlite3.IntegrityError: return False
    except Exception: return False

def get_playlist(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT song_title, song_url FROM user_playlists WHERE user_id = ?", (str(user_id),))
            return cursor.fetchall()
    except Exception: return []

def remove_from_playlist(user_id, song_url):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_playlists WHERE user_id = ? AND song_url = ?", (str(user_id), song_url))
            conn.commit()
        return True
    except Exception: return False

def clear_full_playlist(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_playlists WHERE user_id = ?", (str(user_id),))
            conn.commit()
        return True
    except Exception: return False

# --- MÓDULO DE CROSSHAIRS ---
def add_crosshair(user_id, title, code):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_crosshairs (user_id, title, code) VALUES (?, ?, ?)", (str(user_id), title, code))
            conn.commit()
        return True
    except sqlite3.IntegrityError: return False

def get_crosshairs(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, code FROM user_crosshairs WHERE user_id = ?", (str(user_id),))
            return cursor.fetchall()
    except Exception: return []

def update_crosshair(user_id, title, new_code):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE user_crosshairs SET code = ? WHERE user_id = ? AND title = ?", (new_code, str(user_id), title))
            conn.commit()
            return cursor.rowcount > 0
    except Exception: return False

def delete_crosshair(user_id, title):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_crosshairs WHERE user_id = ? AND title = ?", (str(user_id), title))
            conn.commit()
            return cursor.rowcount > 0
    except Exception: return False

# --- MÓDULO DE SENSIBILIDADES (PRO VERSION) ---

def add_sensitivity(user_id, title, dpi, sens, scoped, ads):
    """Guarda una nueva sensibilidad completa."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_sensitivities (user_id, title, dpi, sens_in_game, scoped_mult, ads_mult) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(user_id), title, dpi, sens, scoped, ads))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_sensitivities(user_id):
    """Obtiene todas las sensibilidades detalladas del usuario."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, dpi, sens_in_game, scoped_mult, ads_mult FROM user_sensitivities WHERE user_id = ?", (str(user_id),))
            return cursor.fetchall()
    except Exception:
        return []

def update_sensitivity(user_id, title, new_dpi, new_sens, new_scoped, nueva_ads):
    """Actualiza todos los parámetros de una sensibilidad existente."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_sensitivities 
                SET dpi = ?, sens_in_game = ?, scoped_mult = ?, ads_mult = ? 
                WHERE user_id = ? AND title = ?
            ''', (new_dpi, new_sens, new_scoped, nueva_ads, str(user_id), title))
            conn.commit()
            return cursor.rowcount > 0
    except Exception:
        return False

def delete_sensitivity(user_id, title):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_sensitivities WHERE user_id = ? AND title = ?", (str(user_id), title))
            conn.commit()
            return cursor.rowcount > 0
    except Exception:
        return False