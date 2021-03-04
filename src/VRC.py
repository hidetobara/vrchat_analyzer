import json,datetime,requests,json,math
from requests.auth import HTTPBasicAuth
from src.Config import Config, dt2str, str2dt

API_BASE = "https://api.vrchat.cloud/api/1"
USER_AGENT = "search-bot"

class VrcWorld:
    def __init__(self):
        self.name = None
        self.id = None
        self.description = None
        self.author_name = None
        self.author_id = None
        self.tags = []
        self.created_at = None # hard to use...
        self.updated_at = None
        self.crawled_at = None
        self.published_at = None # may be published in labs
        self.release_status = None # hidden if the world is deleted
        self.visits = 0
        self.favorites = 0
        self.thumbnail_image_url = None
        self.heat = 0
        self.platforms = None

        self.adjusted_value = None

    def is_public(self):
        return self.release_status == 'public'

    def set_deleted(self):
        now = datetime.datetime.now()
        self.updated_at = now
        self.crawled_at = now
        self.release_status = 'hidden'

    def to_bq(self):
        return {'id':self.id, 'name':self.name, 'author_id':self.author_id, 'author_name':self.author_name,
            'description':self.description, 'tags':'|'+'|'.join(self.tags)+'|',
            'created_at':self.created_at.strftime('%Y-%m-%d %H:%M:%S'), 'updated_at':self.updated_at.strftime('%Y-%m-%d %H:%M:%S'), 'crawled_at':self.crawled_at.strftime('%Y-%m-%d %H:%M:%S'),
            'published_at':None if self.published_at is None else self.published_at.strftime('%Y-%m-%d %H:%M:%S'),
            'release_status':self.release_status,
            'visits':self.visits, 'favorites':self.favorites, 'thumbnail_image_url':self.thumbnail_image_url}
    def to_web(self):
        return {'id':self.id, 'name':self.name, 'description':self.description, 'author_name':self.author_name,
        'thumbnail_image_url':self.thumbnail_image_url,
        'launch_url':"https://www.vrchat.com/home/launch?worldId={}".format(self.id)}
    def to_tsv(self):
        return [
            self.id if str(self.id) is not None else "",
            self.name if self.name is not None else "",
            self.author_name if self.author_name is not None else "",
            self.description if self.description is not None else "",
            json.dumps({'thumbnail_image_url': self.thumbnail_image_url})
        ]

    def how_many_days_passed(self):
        now = datetime.datetime.now()
        born_at = self.created_at if self.published_at is None else self.published_at
        return math.sqrt((now - born_at).days ** 2 + (now - self.updated_at).days ** 2 + 1)

    def fresh_value(self):
        return (math.sqrt(self.visits) + self.favorites) / (self.how_many_days_passed()**1.5)
    def worth_value(self):
        return (math.sqrt(self.visits) + self.favorites) / self.how_many_days_passed()
    def adjust_value(self):
        if self.adjusted_value is None:
            return self.worth_value()
        else:
            return self.adjusted_value(self)

    @staticmethod
    def bq_parse(m):
        i = VrcWorld()
        i.name = m.get('name')
        i.id = m.get('id')
        i.author_name = m.get('author_name')
        i.author_id = m.get('author_id')
        i.created_at = m.get('created_at')
        i.updated_at = m.get('updated_at')
        return i

    @staticmethod
    def parse(m, now=None):
        try:
            i = VrcWorld()
            i.name = m['name']
            i.id = m['id']
            i.author_name = m['authorName']
            i.author_id = m['authorId']
            i.created_at = m['created_at'] if type(m['created_at']) is datetime.datetime else str2dt(m['created_at'][:-5])
            i.updated_at = m['updated_at'] if type(m['updated_at']) is datetime.datetime else str2dt(m['updated_at'][:-5])
            if m['labsPublicationDate'] and m['labsPublicationDate'] != 'none':
                i.published_at = m['labsPublicationDate'] if type(m['labsPublicationDate']) is datetime.datetime else str2dt(m['labsPublicationDate'][:-5])
            elif m['publicationDate'] and m['publicationDate'] != 'none':
                i.published_at = m['publicationDate'] if type(m['publicationDate']) is datetime.datetime else str2dt(m['publicationDate'][:-5])
            i.tags = m['tags']
            i.release_status = m['releaseStatus']
            i.visits = m['visits']
            i.favorites = 0 if 'favorites' not in m else m['favorites']
            i.thumbnail_image_url = m['thumbnailImageUrl']
            i.heat = m['heat']
            i.description = m['description']
            i.crawled_at = datetime.datetime.now() if now is None else now
            i.platforms = []
            for p in m['unityPackages']:
                i.platforms.append(p['platform'])
            i.platforms = list(set(i.platforms))
        except Exception as ex:
            print("ERROR_PARSE=", ex, m)
            return None
        return i

    @staticmethod
    def db_parse(o):
        try:
            i = VrcWorld()
            i.name = o['name']
            i.id = o['id']
            i.author_name = o['author_name']
            i.author_id = o['author_id']
            i.description = o['description']
            i.visits = o['visits'] if 'visits' in o else 0
            i.favorites = o['favorites'] if 'favorites' in o else 0
            return i
        except Exception as ex:
            print("ERROR_PARSE=", ex, o.keys())
            return None

    def __str__(self):
        return json.dumps({k: dt2str(v) if type(v) is datetime.datetime else v for k,v in self.__dict__.items()})

class VrcApi:
    def __init__(self, username, password, debug=False):
        self.logs = []
        self.headers = {'User-Agent': USER_AGENT}
        self.now = datetime.datetime.now()
        try:
            url = "{}/config".format(API_BASE)
            response = requests.get(url, headers=self.headers)
            self.api_key = json.loads(response.text)["clientApiKey"]

            url = "{}/auth/user".format(API_BASE)
            response = requests.get(url, params={"apiKey": self.api_key}, headers=self.headers, auth=HTTPBasicAuth(username, password))
            if debug:
                self.p("response=" + response.text)
                for key, value in response.cookies.items():
                    self.p("cookies[]=" + str(key) + (value))
            self.auth_token = response.cookies["auth"]
        except Exception as ex:
            print("ERROR=", str(ex))

    def p(self, log):
        self.logs.append(log)

    def get_map_world_friends(self):
        worlds = {}
        url = "{}/auth/user/friends".format(API_BASE)
        response = requests.get(url, params={"apiKey": self.api_key, "authToken": self.auth_token}, headers=self.headers)
        friends = json.loads(response.text)
        for f in friends:
            location = f['location']
            if location == 'private':
                continue
            cells = location.split('~')
            instances = cells[0].split(':')
            w = instances[0]
            if not w in worlds:
                worlds[w] = []
            worlds[w].append(f['id'])
        return worlds

    def get_familiar_worlds(self):
        details = []
        for world,users in self.get_map_world_friends().items():
            detail = self.get_world_detail(world)
            if detail is None or not detail.is_public():
                continue
            details.append(detail)
        return details

    def get_popular_worlds(self):
        return self.search_worlds('sort=popularity&featured=false&order=descending&n=30')
    def get_created_worlds(self, last=None):
        return self.search_worlds('sort=created&order=descending&n=30', last)
    def get_updated_worlds(self, last=None):
        return self.search_worlds('sort=updated&order=descending&n=100', last) # &notag=system_labs

    def search_worlds(self, options, last=None):
        details = []
        url = "{}/worlds?{}".format(API_BASE, options)
        response = requests.get(url, params={"apiKey": self.api_key, "authToken": self.auth_token}, headers=self.headers)
        worlds = json.loads(response.text)
        for w in worlds:
            detail = self.get_world_detail(w['id'])
            if detail is None or not detail.is_public():
                continue
            if last is not None and detail.updated_at <= last:
                break
            details.append(detail)
        return details
        
    def get_world_detail(self, wrld):
        url = "{}/worlds/{}".format(API_BASE, wrld)
        try:
            response = requests.get(url, params={"apiKey": self.api_key, "authToken": self.auth_token}, headers=self.headers)
            if response is None or len(response.text) == 0:
                return None
            return VrcWorld.parse(json.loads(response.text), self.now)
        except Exception as ex:
            print("ERROR=", str(ex), "wrld=" + wrld)
            return None
