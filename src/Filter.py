import gspread,json,re
from oauth2client.service_account import ServiceAccountCredentials 


class FilterOption:
    ID = 'id'
    AUTHOR = 'author_id'
    TEXT = 'name_or_description' # for name or description
    RE_TEXT = 'regular_expression'

    def __init__(self, key, value):
        self.key = key
        self.value = None
        self.pattern = None
        if key != FilterOption.RE_TEXT:
            self.value = value
        else:
            self.pattern = re.compile(value, flags=re.IGNORECASE)
    def is_matched(self, w):
        try:
            if self.key == FilterOption.ID:
                return w.id == self.value
            elif self.key == FilterOption.AUTHOR:
                return w.author_id == self.value
            elif self.key == FilterOption.TEXT:
                return (w.name and self.value in w.name) or (w.description and self.value in w.description)
            elif self.key == FilterOption.RE_TEXT:
                return (w.name and self.pattern.search(w.name)) or (w.description and self.pattern.search(w.description))
            return False
        except Exception as ex:
            print("ERROR=", ex, "WORLD=", w)
            return True

class Filter:
    def __init__(self):
        self.whites = []
        self.blacks = []

    def is_passed(self, w):
        _is_passed = True
        for o in self.blacks:
            if o.is_matched(w):
                _is_passed = False
                break
        if _is_passed:
            return True
        for o in self.whites:
            if o.is_matched(w):
                return True
        return False

    def add_black(self, key, value):
        self.blacks.append(FilterOption(key, value))
    def add_white(self, key, value):
        self.whites.append(FilterOption(key, value))

    def import_from_spread_sheet(self, key):
        ss = SpreadSheet(key)
        for row in ss.get_blacks():
            if len(row) < 2: continue
            self.add_black(row[0], row[1])
        for row in ss.get_whites():
            if len(row) < 2: continue
            self.add_white(row[0], row[1])
        print("KEY=", key, "BLACKS=", len(self.blacks), "WHITES=", len(self.whites))

class SpreadSheet:
    def __init__(self, key):
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('./private/vrchat-analyzer-ba2bcb1497e6.json', scope)
        self.gc = gspread.authorize(credentials)
        self.key = key

    def get_blacks(self):
        worksheet = self.gc.open_by_key(self.key).worksheet('black')
        return worksheet.get_all_values()

    def get_whites(self):
        worksheet = self.gc.open_by_key(self.key).worksheet('white')
        return worksheet.get_all_values()
