import json
import os
import shutil

from PIL import Image
from dom_feature_extracter import DOMFeatureExtracter

class PatchManager:
    def __init__(self):
        self.data = []
        self.patch_directory = None
        self.tagged = None

    def feed(self, data_id, filename_image, filename_html):
        self.data.append({
            "id": str(data_id),
            "filename_img": filename_image,
            "filename_html": filename_html,
            "dom": DOMFeatureExtracter(filename_html)
        })
    
    def feed_tagged_data(self, tagged_data_filename):
        with open(tagged_data_filename, 'r') as f:
            self.tagged = json.loads(f.read())

    def save_patches_at(self, patch_directory):
        if patch_directory[-1] != '/':
            patch_directory += '/'
        self.patch_directory = patch_directory

    def generate_spec(self, patch_size=96, verbose=False):
        if self.patch_directory is None:
            raise Exception("Patch directory is not specified")

        if self.patch_directory[:-1] not in os.listdir():
            os.mkdir(self.patch_directory)
        for data in self.data:
            if data["id"] not in os.listdir(self.patch_directory):
                os.mkdir(self.patch_directory + "%s/" % data["id"])

        result_spec = {
            "width": patch_size,
            "height": patch_size,
            "root": self.patch_directory,
            "tags": [ {"name": "text"}, {"name": "image"}, {"name": "graph"}, {"name": "ad"}, {"name": "xad"}, {"name": "nothing"}, ],
            "data": []
        }

        for data in self.data:
            cell = {
                "id": data["id"],
                "filename": data["filename_img"].split('/')[-1],
                "width": 0, "height": 0,
                "keywords": data["dom"].salient_keywords()
                "patches": [],
            }

            folder = self.patch_directory + "%s/" % data["id"]
            shutil.copyfile(data["filename_img"], folder + cell["filename"])
            img = Image.open(folder + cell["filename"])
            cell["width"], cell["height"] = img.size

            if verbose:
                print("making patches of %s " % cell["filename"])
                prev = 20

            for i in range(0, cell["width"]-patch_size, patch_size):
                for j in range(0, cell["height"]-patch_size, patch_size):
                    left, top, right, bottom = i, j, i + patch_size - 1, j + patch_size - 1
                    cropped = img.crop((left, top, right + 1, bottom + 1))
                    cropped_filename = "%dx%d.png" % (i//patch_size, j//patch_size)
                    cropped.save(folder + cropped_filename)

                    tags = [0] * len(result_spec["tags"])
                    self.calc_tags(tags, (left, top, right, bottom))

                    dom = data["dom"]
                    x, y = i + patch_size // 2, j + patch_size // 2
                    features = {
                        "cursor": dom.cursor_style(x, y),
                        "aspect_ratio": dom.element_aspect_ratio(x, y),
                        "is_img": dom.is_img(x, y),
                        "is_iframe": dom.is_iframe(x, y),
                        "nested_a_tags": dom.num_nested_a_tags(x, y),
                        "contains_harmful_url": dom.has_harmful_url_segment(x, y),
                    }

                    cell["patches"].append({
                        "filename": cropped_filename,
                        "left": i,
                        "top": j,
                        "right": i + patch_size - 1,
                        "bottom": j + patch_size - 1,
                        "tags" : tags,
                        "features": features,
                    })
                    if verbose and (i*cell["height"]+j)/cell["height"]/cell["width"] > prev/100:
                        print("... %d%% done" % prev)
                        prev += 20
            result_spec["data"].append(cell)

        return json.dumps(result_spec, indent=4)

    def calc_tags(self, tags, patch):
        l, u, r, d = patch
        patch_area = (r - l) * (d - u)
        for screenshot_id, rects in self.tagged:
            for rect in rects:
                try:
                    ll = rect["left"]
                    uu = rect["top"]
                    rr = rect["left"] + rect["width"]
                    dd = rect["top"] + rect["height"]
                except TypeError as e: # sometimes None values are in the rect
                    continue
                area = max(0, min(r, rr) - max(l, ll)) * max(0, min(d, dd) - max(u, uu))
                tags[rect["type_id"] - 1] += area / patch_area
            tags[-1] = 1 - sum(tags)