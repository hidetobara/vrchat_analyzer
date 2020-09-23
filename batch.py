import argparse
from src.Config import Config
from src.Manager import Manager

c = Config("private/my_account.json")
manager = Manager(c)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--crawl_worlds", help="crawl updated, new-coming worlds", action="store_true")
    parser.add_argument("--update_index", help="update frontend-index", action="store_true")
    args = parser.parse_args()

    if args.crawl_worlds:
        manager.crawl_worlds()
    if args.update_index:
        manager.update_index()
