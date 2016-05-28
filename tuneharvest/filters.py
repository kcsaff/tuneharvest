from urllib.parse import urlparse, parse_qs
from tuneharvest.common import Link


class Masseuse(object):
    SERVICE_NETLOCS = {
        'www.youtube.com': 'youtube',
        'youtu.be': 'youtube',
        'open.spotify.com': 'spotify',
        'play.spotify.com': 'spotify',
    }

    def massage(self, link: Link)-> Link:
        if link.media and not link.service:
            parsed_link = urlparse(link.media)
            service = self.SERVICE_NETLOCS.get(parsed_link.netloc)
            if service:
                link = link._replace(service=service)

        if link.service:
            service_massage = getattr(self, 'massage_{}'.format(link.service), None)
            if service_massage:
                link = service_massage(link)

        return link

    def massage_youtube(self, link: Link)-> Link:
        if link.media and not link.itemid:
            parsed_link = urlparse(link.media)
            qs = parse_qs(parsed_link.query)
            if 'v' in qs:
                link = link._replace(itemid=qs['v'][0])
            elif parsed_link.path:
                link = link._replace(itemid=parsed_link.path.split('/')[-1])
        return link

    def massage_spotify(self, link: Link)-> Link:
        if link.media and not link.itemid:
            parsed_link = urlparse(link.media)
            parts = parsed_link.path.split('/')
            if len(parts) >= 2 and parts[-2] == 'track':
                link = link._replace(itemid=parts[-1])
        return link

