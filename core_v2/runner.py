from __future__ import absolute_import

import psycopg2

from conf import env
from core_v2.download_data import Grepper
from core_v2.saver_psql import (
    get_download_number,
    check_general_existance,
    check_company_existance,
    save_company,
    save_offer,
    save_general,
)


class Runner(Grepper):
    def __init__(self):
        super(Runner, self).__init__()
        try:
            self.connection = psycopg2.connect(
                database=env.DATABASE,
                user=env.USER,
                password=env.PASSWORD,
                host=env.HOST,
                port=env.PORT,
            )
            self.connection.autocommit = False
            print('Successfully connected to database')
        except psycopg2.Error:
            print('Could not open database')
        self.cursor = self.connection.cursor()

    def run(self):
        count = 0
        data_all = self.main()
        timestamp = self.timestamp()
        last_download_number = (get_download_number(self.cursor) or 1) + 1

        for data in data_all:
            company_data = data[0]
            offer_data = data[1]
            # last_download_number = (get_download_number(self.cursor) or 1) + 1
            offer_url_id = offer_data.get('offer_url_id')

            # Check if such record exists already in 'general' table
            exists_general = check_general_existance(
                self.cursor, offer_url_id, last_download_number
            )
            if exists_general:
                continue

            # SAVE offer
            offer_response = save_offer(
                self.cursor,
                self.connection,
                title=offer_data.get('title'),
                salary_to=offer_data.get('salary_to'),
                salary_from=offer_data.get('salary_from'),
                skills=offer_data.get('skills'),
                experience=offer_data.get('experience_level'),
            )
            offer_id = offer_response.get('offer_id')
            if not offer_id:
                print(f'{offer_response["message"]} {offer_response["status"]}')

            # Check if such company already exists in 'company' table
            exists_company_id = check_company_existance(
                self.cursor,
                company_name=company_data.get('name'),
                company_address=company_data.get('address'),
            )

            if not exists_company_id:
                # SAVE company
                company_response = save_company(
                    self.cursor,
                    self.connection,
                    name=company_data.get('name'),
                    city=company_data.get('city'),
                    size=company_data.get('size'),
                    url=company_data.get('website'),
                    address=company_data.get('address'),
                )
                company_id = company_response.get('company_id')

                if not company_id:
                    print(f'{company_response["message"]} {company_response["status"]}')  # noqa

            # SAVE general (last to get id of company and offer)
            general_error = save_general(
                self.cursor,
                self.connection,
                company_id=exists_company_id or company_id,
                offer_id=offer_id,
                timestamp=timestamp,
                download_number=last_download_number,
                offer_url_id=offer_url_id,
            )
            if general_error:
                print(f'{general_error["message"]} {general_error["status"]}')
            print(f'{count+1} Saving offer: {offer_data.get("title")} / {company_data.get("name")}')  # noqa
            count += 1


if __name__ == '__main__':
    import time
    start = time.time()

    r = Runner()
    r.control_amount = env.AMOUNT_CONTROL
    try:
        r.run()
        r.connection.commit()
        print('Saved all successfully ;)')
    except (Exception, psycopg2.DatabaseError) as db_error:
        r.connection.rollback()
        print(f'Error occurred. Could not save. {db_error}')
    r.cursor.close()
    r.connection.close()

    end = time.time()
    print(f'Execution time: {end-start}')
