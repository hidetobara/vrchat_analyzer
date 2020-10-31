import unittest,json
from unittest import TestCase
from src.VRC import VrcWorld

class TestConfig(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_parse(self):
        text = """{
"id": "wrld_bf51e60f-f372-48b1-a757-88ba8331d926",
"name": "Tutorial world",
"description": "This is hoge.",
"featured": false,
"authorId": "usr_38ccf11e-f305-46f2-ae8a-45f74e397a03",
"authorName": "tamsco274",
"capacity": 20,
"tags": ["author_tag_japan", "author_tag_japanese", "admin_approved", "system_approved", "author_tag_jp"],
"releaseStatus": "public",
"imageUrl": "https://api.vrchat.cloud/api/1/file/file_c21e1df5-c53b-4878-b462-608ae900d80b/3/file",
"thumbnailImageUrl": "https://api.vrchat.cloud/api/1/image/file_c21e1df5-c53b-4878-b462-608ae900d80b/3/256",
"assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/140/file",
"assetUrlObject": {},
"pluginUrl": "",
"pluginUrlObject": {},
"unityPackageUrl": "",
"unityPackageUrlObject": {},
"unityPackages": [
    {"id": "unp_ca338897-143c-4ddc-b005-09c5a79e2dd5", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/31/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2017.4.15f1", "unitySortNumber": 20170415000, "assetVersion": 3, "platform": "android", "created_at": "2019-06-19T15:11:54.328Z"}, {"id": "unp_51038d02-a60b-40cb-a65c-b1d408a5741c", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/32/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2017.4.15f1", "unitySortNumber": 20170415000, "assetVersion": 3, "platform": "standalonewindows", "created_at": "2019-06-19T15:15:41.397Z"}, {"id": "unp_22d75e1a-02cb-4f68-9f74-2a4750a4759a", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/84/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2017.4.28f1", "unitySortNumber": 20170428000, "assetVersion": 3, "platform": "android", "created_at": "2020-02-28T12:40:15.238Z"}, {"id": "unp_ee7740cb-acf7-46e1-892a-403aba51edc4", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/87/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2017.4.28f1", "unitySortNumber": 20170428000, "assetVersion": 3, "platform": "standalonewindows", "created_at": "2020-03-01T12:35:10.322Z"}, {"id": "unp_727cafb1-8edb-4be7-a181-62c842a5f493", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/72/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2018.4.11f1", "unitySortNumber": 20180411000, "assetVersion": 3, "platform": "android", "created_at": "2019-12-15T15:01:09.267Z"}, {"id": "unp_4f7aa23d-6fde-40fa-b777-004ffc87f6fc", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/71/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2018.4.11f1", "unitySortNumber": 20180411000, "assetVersion": 3, "platform": "standalonewindows", "created_at": "2019-12-15T14:52:38.453Z"}, {"id": "unp_dbb5a996-7996-42d4-b60d-d18aa0ff13b0", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/105/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2018.4.19f1", "unitySortNumber": 20180419000, "assetVersion": 3, "platform": "android", "created_at": "2020-06-15T12:57:18.855Z"}, {"id": "unp_09213605-0787-4ac8-93ab-75bdf4642811", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/104/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2018.4.19f1", "unitySortNumber": 20180419000, "assetVersion": 3, "platform": "standalonewindows", "created_at": "2020-06-15T12:50:44.795Z"}, {"id": "unp_e082e619-f5cc-46ee-8462-1052f5817b36", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/139/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2018.4.20f1", "unitySortNumber": 20180420000, "assetVersion": 4, "platform": "android", "created_at": "2020-10-29T02:29:42.695Z"}, {"id": "unp_f81bf6c6-e4cb-4f8b-9aee-f3f5a7d44725", "assetUrl": "https://api.vrchat.cloud/api/1/file/file_8e27063c-2bba-4152-8d6d-eb4b812c80d9/140/file", "assetUrlObject": {}, "pluginUrl": "", "pluginUrlObject": {}, "unityVersion": "2018.4.20f1", "unitySortNumber": 20180420000, "assetVersion": 4, "platform": "standalonewindows", "created_at": "2020-10-29T02:33:34.176Z"}
],
"version": 144,
"organization": "vrchat",
"previewYoutubeId": null,
"favorites": 21252,
"created_at": "2018-12-24T07:13:51.540Z",
"updated_at": "2020-10-05T12:31:17.961Z",
"publicationDate": "2019-07-15T20:03:43.582Z",
"labsPublicationDate": "none",
"visits": 1204182,
"popularity": 8,
"heat": 5,
"publicOccupants": 99,
"privateOccupants": 6,
"occupants": 105,
"instances": [["68343", 12]]}"""
        data = json.loads(text)
        instance = VrcWorld.parse(data)
        self.assertEqual('Tutorial world', instance.name)
        self.assertTrue('android' in instance.platforms)
        self.assertTrue('standalonewindows' in instance.platforms)
