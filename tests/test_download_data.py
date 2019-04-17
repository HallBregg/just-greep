import pytest
from freezegun import freeze_time

from core_v1.download_data import Grepper


class TestGrepper:

    @staticmethod
    @freeze_time('2019-03-30 11:42:15')
    def test_timestamp():
        time = Grepper.timestamp()
        assert time == '2019-03-30 11:42:1553942535'

    @pytest.mark.parametrize('skills_offer,skills_detail,expected_result', [
        (
            [{'name': 'Python', 'level': 4}, {'name': 'Cocoa', 'level': 3}],
            [{'name': 'Python', 'level': 4}, {'name': 'Java', 'level': 4}],
            [{'name': 'Python', 'level': 4}, {'name': 'Cocoa', 'level': 3}, {'name': 'Java', 'level': 4}]
        ),
        (
            [{'name': 'Java', 'level': 1}, {'name': 'Kotlin', 'level': 2}],
            [{'name': 'Java', 'level': 1}, {'name': 'Kotlin', 'level': 2}],
            [{'name': 'Java', 'level': 1}, {'name': 'Kotlin', 'level': 2}],
        ),
    ])
    def test_make_skills_unique(self, skills_offer, skills_detail, expected_result):
        result = Grepper.make_skills_unique(skills_offer, skills_detail)
        assert result == expected_result
