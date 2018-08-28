import json

from patch_manager import PatchManager
from tagged_data_fetcher import TaggedDataFetcher

to_exclude = [5, 8, 40, 41, 13, 51, 27, 29, 30, 56]

tag = TaggedDataFetcher("http://52.79.189.93:8005/screenshots/1/export", to_exclude)
with open("test_tagged.txt", "w") as f:
    f.write(json.dumps(tag.id_and_rects()))

print("fetched tagged info")

pm = PatchManager()
for i in range(60):
    if i not in to_exclude:
        pm.feed(i, 'data/%d.png' % i, 'data/%d.txt' % i)
        print("fed %d" % i)
pm.feed_tagged_data('test_tagged.txt')
pm.save_patches_at('test_patches/')
with open('test_spec.json', 'w') as f:
    f.write(pm.generate_spec(verbose=True))