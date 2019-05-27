import requests

offer_url = 'https://justjoin.it/api/offers'


def download_offers():
    """
    Downloads all offers generally
    """
    return requests.get(offer_url).json()


def download_offer_detail(offer_id):
    """
    Downloads detail of offer
    """
    return requests.get(f'{offer_url}/{offer_id}').json()


def unique_skills(general_skills, detail_skills):
    pass


offer_data = {
    'title': None,
    'skills': None
}

offers = download_offers()

for offer in offers:
    offer_detail = download_offer_detail(offer.get('id'))



