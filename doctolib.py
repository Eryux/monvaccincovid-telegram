import cloudscraper
import dateutil.parser
import re

from urllib.parse import urlparse

class DoctolibRequest:

    base_url = "https://www.doctolib.fr/"

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
    
    def get_booking(self, url):
        center = urlparse(url)[2].split('/')[-1]

        r = self._request("booking/{0}.json".format(center))
        if r.status_code == 200:
            return r.json()

        return {}


    def get_availabilities(self, start_date, motive_ids, agendas_ids, practice_ids = [], limit = 4):
        url = "availabilities.json?start_date={0}&visit_motive_ids={1}&agenda_ids={2}&insurance_sector=public&destroy_temporary=true&limit={3}".format(
            start_date, "-".join(motive_ids), "-".join(agendas_ids), limit
        )

        if len(practice_ids) > 0:
            url += "&practice_ids={0}".format("-".join(practice_ids))

        r = self._request(url)
        if r.status_code == 200:
            return r.json()

        return {}


    def _request(self, uri, post_data=None):
        headers = {
            "Accept": "application/json,text/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0 VaccinCovidBot"
        }

        rq = None

        if post_data is not None:
            rq = self.scraper.post(DoctolibRequest.base_url + uri, data = post_data, headers=headers)
        else:
            rq = self.scraper.get(DoctolibRequest.base_url + uri, headers=headers)

        return rq


class DoctolibUtils:

    @staticmethod
    def get_motives_from_ref(motives, ref):
        return [x for x in motives if x['ref_visit_motive_id'] == ref]

    @staticmethod
    def get_agendas_from_motive_and_practice(agendas, motive, practice):
        return [x for x in agendas if motive['id'] in x['visit_motive_ids'] and x['practice_id'] == practice]


    @staticmethod
    def parse_center_url(url):
        parsed_url = urlparse(url)
        
        r = {
            'src': url,
            'clear_url': parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path,
            'name': parsed_url.path.split('/')[-1],
            'practice': -1
        }

        matches = re.search(r'pid=practice-([0-9]+)', parsed_url.query)
        if matches:
            r['practice'] = int(matches.group(1))

        return r


    @staticmethod
    def motives_from_center(center, refs):
        return [x for x in center['data']['visit_motives'] if x['ref_visit_motive_id'] in refs]


    @staticmethod
    def agendas_from_center(center, motive_id, practice_id, can_book = False):
        r = []
        for x in center['data']['agendas']:
            if motive_id in x['visit_motive_ids'] and x['practice_id'] == practice_id:
                if can_book:
                    if x['booking_disabled'] is False and x['booking_temporary_disabled'] is False:
                        r.append(x)
                else:
                    r.append(x)
        return r


    @staticmethod
    def place_from_center(center, practice_name):
        r = None
        for place in center['data']['places']:
            if place['id'] == practice_name:
                r = place
                break
        return r


    @staticmethod
    def slots_from_availabilities(availabilities):
        data = {}

        if 'availabilities' not in availabilities:
            return data

        for day in availabilities['availabilities']:
            data[day['date']] = []
            for slot in day['slots']:
                if isinstance(slot, dict):
                    if 'date' in slot:
                        data[day['date']].append(dateutil.parser.parse(slot['date']))
                    elif 'start_date' in slot:
                        data[day['date']].append(dateutil.parser.parse(slot['start_date']))
                else:
                    data[day['date']].append(dateutil.parser.parse(slot))

        return data


    @staticmethod
    def create_center_link(center_url, practice_id):
        return "{}?pid=practice-{}".format(center_url, practice_id)

# End of file doctolib.py