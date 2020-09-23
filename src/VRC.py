import json,datetime,requests
from requests.auth import HTTPBasicAuth
from src.Config import Config

API_BASE = "https://api.vrchat.cloud/api/1"
USER_AGENT = "search-bot"

class VrcWorld:
    def __init__(self):
        self.name = None
        self.id = None
        self.description = None
        self.author_name = None
        self.author_id = None
        self.tags = None
        self.created_at = None
        self.updated_at = None
        self.release_status = None
        self.visits = 0
        self.favorites = 0
        self.thumbnail_image_url = None
        self.heat = 0

    def is_public(self):
        return self.release_status == 'public'

    def to_bq(self):
        return {'id':self.id, 'name':self.name, 'author_id':self.author_id, 'author_name':self.author_name,
            'description':self.description, 'tags':'|'+'|'.join(self.tags)+'|',
            'created_at':self.created_at.strftime('%Y-%m-%d %H:%M:%S'), 'updated_at':self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'visits':self.visits, 'favorites':self.favorites}

    def to_web(self):
        return {'name':self.name, 'description':self.description, 'author_name':self.author_name,
        'thumbnail_image_url':self.thumbnail_image_url,
        'launch_url':"https://www.vrchat.com/home/launch?worldId={}".format(self.id)}

    @staticmethod
    def parse(m):
        i = VrcWorld()
        try:
            i.name = m['name']
            i.id = m['id']
            i.author_name = m['authorName']
            i.author_id = m['authorId']
            i.tags = m['tags']
            i.created_at = datetime.datetime.fromisoformat(m['created_at'][:-1])
            i.updated_at = datetime.datetime.fromisoformat(m['updated_at'][:-1])
            i.release_status = m['releaseStatus']
            i.visits = m['visits']
            i.favorites = m['favorites']
            i.thumbnail_image_url = m['thumbnailImageUrl']
            i.heat = m['heat']
            i.description = m['description']
        except Exception as ex:
            i.release_status = 'error'
            i.description = str(ex)
        return i

class VrcApi:
    def __init__(self, username, password, debug=False):
        self.logs = []
        self.headers = {'User-Agent': USER_AGENT}
        try:
            url = "{}/config".format(API_BASE)
            response = requests.get(url, headers=self.headers)
            self.api_key = json.loads(response.text)["clientApiKey"]

            url = "{}/auth/user".format(API_BASE)
            response = requests.get(url, params={"apiKey": self.api_key}, headers=self.headers, auth=HTTPBasicAuth(username, password))
            if debug:
                self.p(["response=", response.text])
                for key, value in response.cookies.items():
                    self.p(["cookies[]=", key, value])
            self.auth_token = response.cookies["auth"]
        except Exception as ex:
            self.p(str(ex))

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
            if not detail.is_public():
                continue
            details.append(detail)
        return details

    def get_popular_worlds(self):
        return self.search_worlds('sort=popularity&featured=false&order=descending&n=30')
    def get_created_worlds(self):
        return self.search_worlds('sort=created&order=descending&n=30')
    def get_published_worlds(self):
        return self.search_worlds('sort=updated&order=descending&n=30&notag=system_labs')

    def search_worlds(self, options):
        details = []
        url = "{}/worlds?{}".format(API_BASE, options)
        response = requests.get(url, params={"apiKey": self.api_key, "authToken": self.auth_token}, headers=self.headers)
        worlds = json.loads(response.text)
        for w in worlds:
            detail = self.get_world_detail(w['id'])
            details.append(detail)
        return details
        
    def get_world_detail(self, wrld):
        url = "{}/worlds/{}".format(API_BASE, wrld)
        response = requests.get(url, params={"apiKey": self.api_key, "authToken": self.auth_token}, headers=self.headers)
        return VrcWorld.parse(json.loads(response.text))
