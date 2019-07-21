import psycopg2


class DatabaseSaveError(Exception):
    pass


class DatabaseExistenceError(Exception):
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
        WHERE (name=%s AND street=%s AND url=%s)
    '''
    try:
        cursor.execute(sql, (name, street, url))
        return cursor.fetchone()[0]

    except TypeError:
        return None

    except psycopg2.DatabaseError as db_error:
        raise DatabaseExistenceError(
            f'Could not detect if company {name} exists: {db_error}'
        )

# TODO Create class with save function
# and overrite it with each save like: offer, company, general
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
    # No url_id that why we need loop like this
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
        return int(cursor.fetchone()[0])

    except psycopg2.DatabaseError as db_error:
        raise DatabaseSaveError(
            f'Could not save offer {offer_data.get("title")}: {db_error}'
        )


def save_company(cursor, company_data, other_data):
    """Save company data and return its id"""
    sql = '''
        INSERT INTO company (
            id, name, size, country, city, street, url, longitude, latitude
        )
        VALUES (default, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    '''

    # TODO
    # We need different solution here. Prefarably .values() on dict or .get()
    data_dict = {**company_data, **other_data}
    fields = [
        'name', 'size', 'country', 'city',
        'street', 'url', 'longitude', 'latitude'
    ]
    data = list()
    for field in fields:
        data.append(data_dict.get(field))
    try:
        cursor.execute(sql, (data))
        return int(cursor.fetchone()[0])
    except psycopg2.DatabaseError as db_error:
        raise DatabaseSaveError(
            f'Could not save company {company_data.get("name")}: {db_error}'
        )


# def save_general(offer_id, company_id, url_id, published, download_date):
def save_general(cursor, **kwargs):
    """Save general table"""
    sql = '''
        INSERT INTO general (
            id, offer_id, company_id, url_id, download_number, published, download_date
        )
        VALUES (default, %s, %s, %s, %s, %s, %s)
    '''
    try:
        cursor.execute(sql, (list(kwargs.values())))
    except psycopg2.DatabaseError as db_error:
        raise DatabaseSaveError(
            f'Could not save general data: {db_error}'
        )

def get_last_download_number(cursor):
    """Return last download number from general table"""
    sql = '''
        SELECT MAX(download_number) FROM general;
    '''
    cursor.execute(sql)
    return cursor.fetchone()[0]
