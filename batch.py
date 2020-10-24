import argparse
from src.Config import Config
from src.Manager import Manager

c = Config("private/my_account.json")
manager = Manager(c)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--crawl_worlds", help="crawl updated worlds", action="store_true")
    parser.add_argument("--update_index", help="update frontend-index", action="store_true")
    parser.add_argument("--update_new_coming", help="update new coming", action="store_true")
    parser.add_argument("--insert_world", default=None, help="insert the world")
    args = parser.parse_args()

    if args.crawl_worlds:
        manager.crawl_worlds()
    if args.update_index:
        manager.update_index()
    if args.update_new_coming:
        manager.update_new_coming()
    if args.insert_world is not None:
        manager.insert_world(args.insert_world)

