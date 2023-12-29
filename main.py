import psycopg2
def create_db(cur):
    # Функция, создающая структуру БД (таблицы)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS client_db(
    client_id INTEGER PRIMARY KEY,
    first_name VARCHAR(40) NOT NULL,
    last_name VARCHAR(40) NOT NULL,
    email VARCHAR(100) NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS number_phones(
    phone_id INTEGER PRIMARY KEY,
    phone_client_id INTEGER NOT NULL REFERENCES client_db(client_id),
    phone VARCHAR(12) NOT NULL
    );
    """)


def new_client_add(cur, first_name, last_name, email, phone):
    # Функция, позволяющая добавить нового клиента
    cur.execute("""
    INSERT INTO client_db(first_name, last_name, email) 
    VALUES(?, ?, ?);""", (first_name, last_name, email))
    client_id = cur.lastrowid  # Получаем ID нового клиента

    cur.execute("""
    INSERT INTO number_phones(phone_client_id, phone)
    VALUES(?, ?);""", (client_id, phone))


def add_phone(cur, client_id, phone):
    # Функция, позволяющая добавить телефон для существующего клиента
    cur.execute("""
    INSERT INTO number_phones(phone_client_id, phone)
    VALUES(?, ?);
    """, (client_id, phone))


def changed_client(cur, client_id, first_name=None, last_name=None, email=None, phone=None):
    # Функция, позволяющая изменить данные о клиенте
    update_params = {}
    if first_name is not None:
        update_params['first_name'] = first_name
    if last_name is not None:
        update_params['last_name'] = last_name
    if email is not None:
        update_params['email'] = email

    if update_params:
        update_query = f"UPDATE client_db SET {', '.join(f'{key}=?' for key in update_params)} WHERE client_id=?;"
        cur.execute(update_query, tuple(update_params.values()) + (client_id,))

    if phone is not None:
        cur.execute("""
        UPDATE number_phones SET phone=? WHERE phone_client_id=?;
        """, (phone, client_id))


def delete_phone(cur, client_id, phone):
    # Функция, позволяющая удалить телефон для существующего клиента
    cur.execute("""
    DELETE FROM number_phones WHERE phone_client_id=? AND phone=?;
    """, (client_id, phone))


def delete_client(cur, client_id):
    # Функция, позволяющая удалить существующего клиента
    cur.execute("""
    DELETE FROM client_db WHERE client_id=?;
    """, (client_id,))


def find_client(cur, first_name='%', last_name='%', email='%', phone='%'):
    # Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
    cur.execute("""
    SELECT * FROM client_db WHERE first_name LIKE ? AND last_name LIKE ? AND email LIKE ?;
    """, (first_name, last_name, email))

    client_results = cur.fetchall()

    cur.execute("""
    SELECT * FROM number_phones WHERE phone LIKE ?;
    """, (phone,))
    phone_results = cur.fetchall()

    return client_results, phone_results

if __name__ == "__main__":
    with psycopg2.connect(database="client_db", user="postgres", password="") as conn:
        cur = conn.cursor()
        create_db(cur)
        new_client_add(cur, 'Алекс', 'Иванов', 'alexivanov@yandex.ru', '89960786556')
        new_client_add(cur, 'Алиса', 'Иванова', 'alisivanova@yandex.ru', '55550005500')
        add_phone(cur, 1, '86754890432')
        changed_client(cur, 2, first_name='Элис')
        delete_phone(cur, 1, '89960786556')
        delete_client(cur, 2)
        print(find_client(cur, 'Алекс', 'Иванов', 'alexivanov@yandex.ru', '86754890432'))