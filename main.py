import psycopg2

#Функция, создающая структуру БД (таблицы)
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS client_db(
        client_id SERIAL PRIMARY KEY,
        first_name VARCHAR(40) NOT NULL,
        last_name VARCHAR(40) NOT NULL,
        email VARCHAR(100) NOT NULL
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS number_phones(
        phone_id SERIAL PRIMARY KEY,
        phone_client_id INTEGER NOT NULL REFERENCES client_db(client_id),
        phone VARCHAR(12) NOT NULL
        );
        """)

        return cur.fetchall()
#Функция, позволяющая добавить нового клиента
def new_client_add(conn, first_name, last_name, email, phone=None):
    with conn.cursor() as cur:
        cur.execute(f"""
        INSERT INTO client_db(first_name, last_name, email) 
        VALUES(%s, %s, %s, %s);
        """,(first_name, last_name, email,))

        cur.execute(f"""
        INSERT INTO number_phones(phone) 
        VALUES(%s);
        """,(phone,))
        return cur.fetchall()

#Функция, позволяющая добавить телефон для существующего клиента
def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute(f"""
        INSERT INTO number_phones(phone) WHERE (SELECT client_id FROM client_db)
        VALUES(%s, %s);
        """,(client_id, phone,))
        return cur.fetchall()

#Функция, позволяющая изменить данные о клиенте
def changed_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute(f"""
        UPDATE client_db SET first_name=%s OR last_name=%s OR email=%s WHERE client_id=%s;
        """,(client_id, first_name, last_name, email,))

        cur.execute(f"""
        UPDATE number_phones(phone) WHERE (SELECT client_id=s% FROM client_db);
        """,(phone,))

        return cur.fetchall()


#Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute(f"""
        DELETE FROM number_phones WHERE (SELECT client_id=%s FROM client_db);
        """,(client_id, phone,))
        return cur.fetchall()


#Функция, позволяющая удалить существующего клиента
def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute(f"""
        DELETE FROM client_db WHERE client_id=%s;
        """,(client_id,))
        return cur.fetchall()


#Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
def find_client(conn, first_name='%', last_name='%', email='%', phone='%'):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT * FROM client_db WHERE first_name LIKE '%' 
        AND last_name LIKE '%' 
        AND email LIKE '%';
        """,(first_name, last_name, email))

        cur.execute("""
        SELECT * FROM number_phones WHERE phone LIKE '%';
        """,(phone))
        return cur.fetchall()

with psycopg2.connect(database="client_db", user="postgres", password="") as conn:
    if __name__ == "__main__":
        create_db(conn)
        new_client_add(conn, 'Алекс', 'Иванов', 'alexivanov@yandex.ru', '89960786556')
        new_client_add(conn, 'Алиса', 'Иванова', 'alisivanova@yandex.ru', '55550005500')
        add_phone(conn, '1', '86754890432')
        changed_client(conn, '2', 'Элис', None, None, None)
        delete_phone(conn, '1', '89960786556')
        delete_client(conn, '2')
        print(find_client(conn, 'Алекс', 'Иванов', 'alexivanov@yandex.ru', '86754890432'))

conn.close()