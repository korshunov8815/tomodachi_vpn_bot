import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

DATABASE = "tomodachi.db"


def get_db_connection():
    return sqlite3.connect(DATABASE)


def insert_user(user):
    try:
        with get_db_connection() as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT user_id FROM users WHERE telegram_id=?", (user.id,))
            if res.fetchone() is None:
                first_name = user.first_name if user.first_name else "NULL"
                last_name = user.last_name if user.last_name else "NULL"
                username = user.username if user.username else "NULL"
                cur.execute(
                    "INSERT INTO users (telegram_id, first_name, last_name, username, is_trial) VALUES(?, ?, ?, ?, 1)",
                    (user.id, first_name, last_name, username)
                )
                con.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Exception in insert_user: {e}")


def is_trial(id):
    try:
        with get_db_connection() as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT is_trial FROM users WHERE telegram_id=?", (id,))
            result = res.fetchone()
            if result:
                return result[0]
            return None
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None
    except Exception as e:
        logging.error(f"Exception in is_trial: {e}")
        return None


def close_trial(id):
    try:
        with get_db_connection() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE users SET is_trial = 0 WHERE telegram_id=?", (id,))
            con.commit()
            return True
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return False
    except Exception as e:
        logging.error(f"Exception in close_trial: {e}")
        return False


def insert_key(name, key_server_id, access_url, api, telegram_id, data_limit, is_free):
    try:
        with get_db_connection() as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT server_id FROM servers WHERE url=?", (api,))
            server_id = res.fetchone()
            if not server_id:
                logging.error("Server not found")
                return False
            server_id = server_id[0]

            res = cur.execute(
                "SELECT user_id FROM users WHERE telegram_id=?", (telegram_id,))
            user_id = res.fetchone()
            if not user_id:
                logging.error("User not found")
                return False
            user_id = user_id[0]

            expiration = "+7 days" if is_free else "+1 months"
            cur.execute(
                "INSERT INTO keys (key_name, outline_server_id, key_server_id, access_url, user_id, expiration, data_limit, is_free, is_expired) "
                "VALUES(?, ?, ?, ?, ?, datetime('now', ?), ?, ?, 0)",
                (name, server_id, key_server_id, access_url,
                 user_id, expiration, data_limit, is_free)
            )
            con.commit()
            return True
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return False
    except Exception as e:
        logging.error(f"Exception in insert_key: {e}")
        return False


def find_expired_keys():
    try:
        with get_db_connection() as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT key_id, outline_server_id, key_server_id, telegram_id, key_name "
                "FROM keys INNER JOIN users ON users.user_id = keys.user_id "
                "WHERE is_expired=0 AND expiration < datetime('now')"
            )
            result = res.fetchall()
            for key in result:
                cur.execute(
                    "UPDATE keys SET is_expired = 1 WHERE key_id=?", (key[0],))
                con.commit()
            return result
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return []
    except Exception as e:
        logging.error(f"Exception in find_expired_keys: {e}")
        return []


def get_single_server(location):
    try:
        with get_db_connection() as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT url FROM servers WHERE location=?", (location,))
            result = res.fetchone()
            if result:
                return result[0]
            return None
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None
    except Exception as e:
        logging.error(f"Exception in get_single_server: {e}")
        return None


def get_server_locations():
    try:
        with get_db_connection() as con:
            cur = con.cursor()
            res = cur.execute("SELECT location FROM servers")
            result = res.fetchall()
            return result
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return []
    except Exception as e:
        logging.error(f"Exception in get_server_locations: {e}")
        return []


def get_user_keys(telegram_id):
    try:
        with get_db_connection() as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT user_id FROM users WHERE telegram_id=?", (telegram_id,))
            user_id = res.fetchone()
            if not user_id:
                logging.error("User not found")
                return []
            user_id = user_id[0]

            res = cur.execute(
                "SELECT key_id, key_name, outline_server_id, key_server_id, access_url, user_id, expiration, data_limit, is_free, is_expired "
                "FROM keys WHERE user_id=? AND is_expired=0", (user_id,)
            )
            result = res.fetchall()
            return result
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return []
    except Exception as e:
        logging.error(f"Exception in get_user_keys: {e}")
        return []


def save_preferred_server(telegram_id, location):
    try:
        with get_db_connection() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE users SET wants_server = ? WHERE telegram_id=?", (location, telegram_id))
            con.commit()
            return True
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return False
    except Exception as e:
        logging.error(f"Exception in save_preferred_server: {e}")
        return False
