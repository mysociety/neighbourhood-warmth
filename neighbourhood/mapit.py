from django.conf import settings

from requests_cache import CachedSession

session = CachedSession(cache_name=settings.CACHE_FILE, expire_after=86400)


class BaseException(Exception):
    pass


class NotFoundException(BaseException):
    pass


class BadRequestException(BaseException):
    pass


class InternalServerErrorException(BaseException):
    pass


class ForbiddenException(BaseException):
    pass


class MapIt(object):
    postcode_url = "%s/postcode/%s?api_key=%s"
    cache = {}

    def __init__(self):
        self.base = settings.MAPIT_URL

    def postcode_point_to_centroid(self, pc):
        url = self.postcode_url % (self.base, pc, settings.MAPIT_API_KEY)
        data = self.get(url)
        return {"lat": data["wgs84_lat"], "lon": data["wgs84_lon"]}

    def postcode_point_to_data(self, pc):
        url = self.postcode_url % (self.base, pc, settings.MAPIT_API_KEY)
        data = self.get(url)
        return data

    def get(self, url):
        if url not in self.cache:
            resp = session.get(url)
            data = resp.json()
            if resp.status_code == 403:
                raise ForbiddenException(data["error"])
            if resp.status_code == 500:
                raise InternalServerErrorException(data["error"])
            if resp.status_code == 404:
                raise NotFoundException(data["error"])
            if resp.status_code == 400:
                raise BadRequestException(data["error"])
            self.cache[url] = data
        return self.cache[url]
