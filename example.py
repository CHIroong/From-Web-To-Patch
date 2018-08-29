import json

from patch_manager import PatchManager
from tagged_data_fetcher import TaggedDataFetcher

to_exclude = [5, 8, 40, 41, 13, 51, 27, 29, 30, 38, 56, 11] + [1, 4, 22, 23, 28, 34, 36, 43, 45]

tag = TaggedDataFetcher("http://52.79.189.93:8005/screenshots/1/export", to_exclude)
with open("tagged.txt", "w") as f:
    f.write(json.dumps(tag.id_and_rects()))

print("fetched tagged info")

pm = PatchManager()
for i in range(1, 60+1):
    if i not in to_exclude:
        pm.feed(i, 'data/%d.png' % (i-1), 'data/%d.txt' % (i-1))
        print("fed %d" % i)
pm.feed_tagged_data('tagged.txt')
pm.save_patches_at('patches/')
with open('spec.json', 'w') as f:
    f.write(pm.generate_spec(verbose=True))