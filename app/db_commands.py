
class DatabaseSaveError(Exception):
    pass


class DatabaseExistanceError(Exception):
    pass


def check_general_existance(cursor, url_id, download_number):
    """Check if general connection exists"""
    sql = '''
        SELECT EXISTS(
            SELECT url_id, download_number
            FROM general WHERE url_id=%s AND download_number=%s
        );
    '''
    cursor.execute(sql, (url_id, download_number))
    return cursor.fetchone()[0]


def check_company_existance(cursor, name, street, url):
    """Check if company already exists. If so return its id"""
    sql = '''
        SELECT id
        FROM company
        WHERE (name=%s AND street=%s AND url=%s
    '''
    try:
        cur.execute(sql, (name, street, url))
        return cur.fetchone()[0]

    except TypeError:
        return None

    except psycopg2.DatabaseError:
        raise DatabaseExistanceError(
            f'Could not detect if company {name} exists'
        )

def save_offer(cursor, offer_data):
    """Save offer data and return its id"""
    sql = '''
        INSERT INTO offer (
            id, title, skills, remote, salary_from, salary_to, salary_currency, experience, body
        )
        VALUES (default, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    '''
    # TODO
    # How to auto-assign. Loop through dict .keys() .values() ???
    # Maybe some fancy data structure?
    fields = [
        'title', 'skills', 'remote',
        'salary_from', 'salary_to', 'salary_currency',
        'experience', 'body'
    ]
    data = list()
    for field in fields:
        data.append(offer_data.get(field))
    try:
        cursor.execute(sql, (data))
        return cursor.fetchone()[0]

    except psycopg2.DatabaseError as db_error:
        raise DatabaseSaveError(
            f'Could not save offer {offer_data.get("title")}: {db_error}'
        )


def get_last_download_number(cursor):
    """Return last download number from general table"""
    sql = '''
        SELECT MAX(download_number) FROM general;
    '''
    cursor.execute(sql)
    return cursor.fetchone()[0]
