from datetime import datetime
import json
import psycopg2
import random
import re
import requests
import time

import db_commands as db_exec


offers_url = 'https://justjoin.it/api/offers'
offer_url = 'https://justjoin.it/api/offers/{}'

# TODO make this code more OOP


def check_db():
    # TODO change to os.environ
    conn = psycopg2.connect(
        host='db',
        port='5432',
        dbname='app',
        user='postgres',
        password='postgres'
    )
    try:
        cur = conn.cursor()
        cur.close()
        conn.close()
        return True
    except (psycopg2.DatabaseError, psycopg2.OperationalError):
        print('Database error')
        return False


def random_sleep():
    """Random sleep for safe download purposes (simulate human activity)"""
    time.sleep(round(random.random(), 4))


def format_skills(general_skills, detail_skills):
    """Returns list of unique dicts of skills and levels"""
    unique_skills = list()
    skills = general_skills + detail_skills
    for skill in skills:
        if skill not in unique_skills:
            skill['name'] = skill['name'].lower()
            unique_skills.append(skill)
    return json.dumps(unique_skills)


def format_date(date):
    """Changes string data to datetime object"""
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")


def format_body(body):
    """Returns string of body without html chars"""
    regex = re.compile('<.*?>')
    return re.sub(regex, '', body).replace('&nbsp', '').replace(';', ' ')


def download_offers():
    """Download list of all offers from main page"""
    return requests.get(offers_url).json()


def download_specific_offer(offer_url_id):
    """Download specific offer"""
    return requests.get(offer_url.format(offer_url_id)).json()


def get_download_number(cursor):
    """Return active downalod_number"""
    last_download_number = db_exec.get_last_download_number(cursor)
    if not last_download_number:
        return 1
    return last_download_number + 1


def handle(debug=False, cursor=None, save=True, **kwargs):
    """Main function. Core of JustGreep"""
    offers = download_offers()
    offers_count = len(offers)
    download_number = get_download_number(cursor)
    download_date = datetime.now()
    count = 0

    for offer in offers:
        offer_url_id = offer.get('id')
        if not offer_url_id:
            # skip the loop if no id (ipossible ?)
            continue

        offer_detail = download_specific_offer(offer_url_id)

        offer_data = {
            'title': offer_detail.get('title'),
            'skills': format_skills(offer_detail.get('skills'), offer.get('skills')),  # noqa
            'remote': offer_detail.get('remote'),
            'salary_from': offer_detail.get('salary_from'),
            'salary_to': offer_detail.get('salary_to'),
            'salary_currency': offer_detail.get('salary_currency'),
            'experience': offer_detail.get('experience_level'),
            'url_id': offer_detail.get('id'),
            'body': format_body(offer_detail.get('body')),
        }
        company_data = {
            'country': offer_detail.get('country_code').lower(),
            'url': offer_detail.get('company_url'),
            'size': offer_detail.get('company_size'),
            'name': offer_detail.get('company_name'),
            'city': offer_detail.get('city').lower(),
            'street': offer_detail.get('street').lower(),
        }
        other_data = {
            'clause_data': offer_detail.get('information_clause'),
            'latitude': offer_detail.get('latitude'),
            'longitude': offer_detail.get('longitude'),
            'published': format_date(offer_detail.get('published_at')),
        }

        if debug:
            if count == kwargs.get('count_limit'):
                break
            count += 1
            print(f'{count}/{offers_count} {offer_data["title"]} - {company_data["name"]}')  # noqa

        if save:
            if db_exec.check_general_existance(
                cursor, offer_data['url_id'], download_number-1
            ):
                # if record already exists, skip loop
                continue

            # offer save
            offer_id = int()
            try:
                offer_id = db_exec.save_offer(cursor, offer_data)
            except db_exec.DatabaseSaveError as db_error:
                print(f'{db_error}')
                break # continue?

            # company existance
            company_id = int()
            try:
                company_id = db_exec.check_company_existance(
                    cursor,
                    company_data.get('name'),
                    company_data.get('street'),
                    company_data.get('url')
                )
            except db_exec.DatabaseExistenceError as db_error:
                print(f'{db_error}')
                break # continue?

            # save company
            if not company_id:
                try:
                    company_id = db_exec.save_company(
                        cursor, company_data, other_data
                    )
                except db_exec.DatabaseSaveError as db_error:
                    print(f'{db_error}')
                    break # continue?

            # TODO connect everything in general table
            general_data = {
                'offer_id': offer_id,
                'company_id': company_id,
                'url_id': offer_data.get('url_id'),
                'download_number': download_number,
                'published': other_data.get('published'),
                'download_date': download_date
            }
            try:
                db_exec.save_general(cursor=cursor, **general_data)
            except db_exec.DatabaseSaveError as db_error:
                print(f'{db_error}')
                break;

        # Simulate human activity
        random_sleep()

if __name__ == '__main__':
    debug = True
    # TODO fix db checking, plan this
    if check_db():
        conn = psycopg2.connect(
            host='db',
            port='5432',
            dbname='app',
            user='postgres',
            password='postgres'
        )
        cursor = conn.cursor()
        handle(debug, cursor, count_limit=None)
        conn.commit()
        conn.close()
        cursor.close()
