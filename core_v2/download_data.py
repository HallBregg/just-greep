from __future__ import absolute_import

from datetime import datetime
import json
import random
import requests
import time


class Grepper:

    def __init__(self):
        self.url = 'https://justjoin.it/api/offers'
        self.control_amount = False

    def download_main(self):
        """Download all offers generally"""
        response = requests.get(self.url)
        return response.json()

    def download_detail(self, url_detail_id):
        """Download detailed data of offer"""
        url = f'{self.url}/{url_detail_id}'
        response = requests.get(url)
        return response.json()

    @staticmethod
    def timestamp():
        """Returns datetime.now()"""
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d %H:%M:%s')
        return date_time

    @staticmethod
    def make_skills_unique(skills_offer, skills_detail):
        """Create list of unique skills dict elements"""
        all_skills = skills_offer + skills_detail
        unique_skills = ''
        for skill in all_skills:
            name = skill.get('name').lower()
            level = skill.get('level')
            skill_obj = f'{name}:{level},'
            if skill_obj not in unique_skills:
                unique_skills += skill_obj
        return unique_skills

    @staticmethod
    def generate_random_time():
        return round(random.random(), 4)

    def main(self):
        """
        Dowloads data and greps certain data,
        and returns it in list of tuples.
        """
        main_data = self.download_main()
        all_list = []
        count = 0
        for offer in main_data:
            print(f'{count+1}/{len(main_data)} downloading {offer["title"]}')
            detail_url_id = offer.get('id')
            detailed_data = self.download_detail(detail_url_id)
            offer_skills = offer.get('skills')
            detailed_skills = detailed_data.get('skills')

            company_data = {
                'name': offer.get('company_name').lower(),
                'city': offer.get('city').lower(),
                'address': offer.get('address_text').lower(),
                'size': offer.get('company_size'),
                'website': offer.get('company_url'),
            }
            offer_data = {
                'title': detailed_data.get('title'),
                'salary_from': detailed_data.get('salary_from'),
                'salary_to': detailed_data.get('salary_to'),
                'skills': self.make_skills_unique(offer_skills, detailed_skills),
                'experience_level': detailed_data.get('experience_level'),
                'offer_url_id': detailed_data.get('id'),
            }
            all_list.append((company_data, offer_data))
            count += 1
            # amount controller
            if self.control_amount:
                if self.control_amount == count:
                    break

            time.sleep(self.generate_random_time())

        return all_list


if __name__ == '__main__':
    from conf import env

    grep = Grepper()
    grep.control_amount = env.AMOUNT_CONTROL
    data = grep.main()
    timestamp = grep.timestamp()

    print(f'TIMESTAMP: {timestamp}')
    for obj in data:
        print(f'{obj}\n')
