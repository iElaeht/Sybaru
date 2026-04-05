import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "sybaru_data.db")

def init_db():
    """Crea la tabla de playlists si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_playlists (
            user_id INTEGER,
            song_title TEXT,
            song_url TEXT,
            PRIMARY KEY (user_id, song_url)
        )
    ''')
    conn.commit()
    conn.close()

def save_to_playlist(user_id, title, url):
    """Guarda una canción. Retorna True si se guardó, False si ya existía."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_playlists (user_id, song_title, song_url) VALUES (?, ?, ?)", (user_id, title, url))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error en la DB: {e}")
        return False

def get_playlist(user_id):
    """Recupera todas las canciones de un usuario."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT song_title, song_url FROM user_playlists WHERE user_id = ?", (user_id,))
        data = cursor.fetchall()
        conn.close()
        return data
    except Exception:
        return []

def clear_playlist(user_id):
    """Borra toda la lista del usuario."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_playlists WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al limpiar DB: {e}")
        
def remove_from_playlist(user_id, song_index):
    """Elimina una canción específica basada en su posición en la lista (1-based)."""
    try:
        # Primero obtenemos la canción en esa posición para tener su URL (que es la PK)
        songs = get_playlist(user_id)
        if 0 < song_index <= len(songs):
            target_url = songs[song_index - 1][1] # El índice es -1 porque el usuario ve 1, 2, 3...
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_playlists WHERE user_id = ? AND song_url = ?", (user_id, target_url))
            conn.commit()
            conn.close()
            return True
        return False
    except Exception as e:
        print(f"Error al eliminar de la DB: {e}")
        return False