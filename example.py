import json

from patch_manager import PatchManager
from tagged_data_fetcher import TaggedDataFetcher

tag = TaggedDataFetcher("http://52.79.189.93:8005/screenshots/1/export")
with open("test_tagged.txt", "w") as f:
    f.write(json.dumps(tag.id_and_rects()))

pm = PatchManager()
for i in range(2):
    pm.feed(i, 'data/%d.png' % i, 'data/%d.txt' % i)
pm.feed_tagged_data('test_tagged.txt')
pm.save_patches_at('test_patches/')
with open('test_spec.json', 'w') as f:
    f.write(pm.generate_spec(verbose=True))