import json
import psycopg2
import random
import re
import requests
import time

import db_commands as db_exec


offers_url = 'https://justjoin.it/api/offers'
offer_url = 'https://justjoin.it/api/offers/{}'


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
        return unique_skills


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


def handle(debug=False, save=True, cursor **kwargs):
    """Main function. Core of JustGreep"""
    offers = download_offers()
    offers_count = len(offers)
    last_download_number = db_exec.get_last_download_number(cursor)
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
            'sallary_from': offer_detail.get('sallary_from'),
            'sallary_to': offer_detail.get('sallary_to'),
            'sallary_currency': offer_detail.get('sallary_currency'),
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
            'published': offer_detail.get('published_at'),
        }

        if debug:
            if count == kwargs.get('count_limit'):
                break
            count += 1
            print(f'{count}/{offers_count} {offer_data["title"]} - {company_data["name"]}')  # noqa

        if save:
            if db_exec.check_general_existance(
                cursor, offer_data['url_id'],
                last_download_number
            ):
                # if record already exists, skip loop
                continue
            # TODO add offer



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
        handle(debug, count_limit=10, cursor)
