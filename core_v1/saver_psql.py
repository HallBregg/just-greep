from __future__ import absolute_import

import psycopg2


def get_download_number(cursor):
    sql = '''
        SELECT MAX(download_number)
        FROM general
    '''
    cursor.execute(sql)
    return cursor.fetchone()[0]


def check_general_existance(cursor, offer_url_id, download_number):
    """Returns True if such object exists, False otherwise"""

    sql = '''
        SELECT
        EXISTS(
            SELECT offer_url_id, download_number
            FROM general
            WHERE(offer_url_id=%s AND download_number=%s)
        )
    '''
    cursor.execute(sql, (offer_url_id, download_number))
    return cursor.fetchone()[0]


def check_company_existance(cursor, company_name, company_address):
    sql2 = '''
        SELECT
        EXISTS(
            SELECT name, address
            FROM company
            WHERE (name=%s AND address=%s)
        )
    '''
    sql = '''
        SELECT id FROM company WHERE (name=%s AND address=%s)
    '''
    cursor.execute(sql, (company_name, company_address))
    try:
        return cursor.fetchone()[0]
    except TypeError:
        return None


def save_company(cursor, connection, **params):
    sql = '''
        INSERT INTO company (id, name, city, size, url, address)
        VALUES (default, %s, %s, %s, %s, %s)
        RETURNING id
    '''
    name = params.get('name')
    city = params.get('city')
    size = params.get('size')
    url = params.get('url')
    address = params.get('address')
    try:
        cursor.execute(sql, (name, city, size, url, address))
        # connection.commit()
        response = {'company_id': cursor.fetchone()[0]}
    except psycopg2.DatabaseError as db_error:
        response = {
            'message': f'Could not save company: {name}',
            'status': f'{db_error}'
        }
    return response


def save_offer(cursor, connection, **params):
    sql = '''
        INSERT INTO offer (
            id, title, salary_from, salary_to, skills, experience
        )
        VALUES (default, %s, %s, %s, %s, %s)
        RETURNING id
    '''
    title = params.get('title')
    salary_from = params.get('salary_from')
    salary_to = params.get('salary_to')
    skills = params.get('skills')
    experience = params.get('experience')
    try:
        cursor.execute(sql, (title, salary_from, salary_to, skills, experience))
        # connection.commit()
        response = {'offer_id': cursor.fetchone()[0]}
    except psycopg2.DatabaseError as db_error:
         response = {
            'message': f'Could not save offer: {title}',
            'status': f'{db_error}'
        }
    return response


def save_general(cursor, connection, **params):
    sql = '''
        INSERT INTO general (
            id, company_id, offer_id, timestamp, download_number, offer_url_id
        )
        VALUES (default, %s, %s, %s, %s, %s)
    '''
    company_id = params.get('company_id')
    offer_id = params.get('offer_id')
    timestamp = params.get('timestamp')
    download_number = params.get('download_number')
    offer_url_id = params.get('offer_url_id')
    try:
        cursor.execute(sql, (company_id, offer_id, timestamp, download_number, offer_url_id))  # noqa
        # connection.commit()
    except psycopg2.DatabaseError as db_error:
        return {
            'message': f'Could not save general: {offer_url_id}',
            'status': f'{db_error}'
        }


if __name__ == '__main__':
    connection = psycopg2.connect(
        database='justdb',
        user='halldb',
        password='proxycrypto',
        host='192.168.1.28',
        port='5432'
    )
    cursor = connection.cursor()
    print(check_company_existance(cursor, 'test', 'test'))
    print(check_general_existance(cursor, 4, 1))
    print(get_download_number(cursor))

    connection.close()
