from datetime import datetime
import re
import requests


class Downloader:

    def __init__(self):
        self.offer_url = 'https://justjoin.it/api/offers'
        self.debug = False
        self.count_control = None
        self.save = False

    def download_offers(self):
        """
        Downloads all offers generally
        """
        return requests.get(self.offer_url).json()

    def download_offer_detail(self, offer_id):
        """
        Downloads detail of offer
        """
        return requests.get(f'{self.offer_url}/{offer_id}').json()

    @staticmethod
    def format_skills(general_skills, detail_skills):
        """
        Returns list of unique dicts of skills and levels
        """
        unique_skills = list()
        skills = general_skills + detail_skills
        for skill in skills:
            if skill not in unique_skills:
                skill['name'] = skill['name'].lower()
                unique_skills.append(skill)
        return unique_skills

    @staticmethod
    def format_body(body):
        """
        Returns string of body without html chars
        """
        regex = re.compile('<.*?>')
        return re.sub(regex, '', body).replace('&nbsp', '').replace(';', ' ')

    @staticmethod
    def timestamp():
        """Returns datetime.now()"""
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d %H:%M:%s')
        return date_time

    def format_data(self, offer):
        """
        Get detailed offers and format it into three dicts:
        offer, company, other
        """
        offer_detail = self.download_offer_detail(offer.get('id'))

        offer_data = {
            'title': offer_detail.get('title'),
            'skills': self.format_skills(offer_detail.get('skills'),
                                         offer.get('skills')),  # noqa
            'remote': offer_detail.get('remote'),
            'sallary_from': offer_detail.get('sallary_from'),
            'sallary_to': offer_detail.get('sallary_to'),
            'sallary_currency': offer_detail.get('sallary_currency'),
            'experience': offer_detail.get('experience_level'),
            'id': offer_detail.get('id'),
            'body': self.format_body(offer_detail.get('body')),
        }

        company_data = {
            'country': offer_detail.get('country_code').lower(),
            'url': offer_detail.get('company_url'),
            'size': offer_detail.get('company_size'),
            'name': offer_detail.get('company_name'),
            'city': offer_detail.get('city'),
            'street': offer_detail.get('street'),
        }

        other_data = {
            'clause_data': offer_detail.get('information_clause'),
            'latitude': offer_detail.get('latitude'),
            'longitude': offer_detail.get('longitude'),
            'published': offer_detail.get('published_at'),
        }
        return {
            'offer_data': offer_data,
            'company_data': company_data,
            'other_data': other_data
        }
      
    def main(self):
        offers = self.download_offers()
        timestamp = self.timestamp()
        offers_count = len(offers)
        count = 0
        for offer in offers:
            count += 1
            data = self.format_data(offer)

            if self.debug:
                title = data.get('offer_data')['title']
                company = data.get('company_data')['name']
                print(f'{count}/{offers_count} {title} / {company}')  # noqa
                if self.count_control == count:
                    break

            if self.save:
                pass  # Process save functions


d = Downloader()
d.debug = True
d.main()
                      

