import sys
import json
import requests

from collections import defaultdict

class TaggedDataFetcher:
    def __init__(self, url):
        data = json.loads(requests.get(url).text)
        self.rects_info = defaultdict(list)
        for rect in data["target"]:
            self.rects_info[rect["screenshot_id"]].append(rect)
    
    def has_tagged_info(self, screenshot_id):
        return screenshot_id in self.rects_info
    
    def id_and_rects(self):
        return list(self.rects_info.items())

if __name__ == "__main__":
    with open(sys.argv[2], "w") as f:
        f.write(json.dumps(TaggedDataFetcher(sys.argv[1]).id_and_rects()))