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


def save_offer(cursor, offer_data):
    """Save offer data"""
    sql = '''
        
    '''


def get_last_download_number(cursor):
    """Return last download number from general table"""
    sql = '''
        SELECT MAX(download_number) FROM general;
    '''
    cursor.execute(sql)
    return cursor.fetchone()[0]
