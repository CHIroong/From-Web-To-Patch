import json

from collections import defaultdict

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from easylist import EasyListHandler

class DOMFeatureExtracter:
    def __init__(self, filename):
        self.soup = BeautifulSoup(open(filename, "r", encoding='UTF-8').read(), 'html.parser')
        self.filename = filename
        self.point_data = json.loads(self.soup.body["sg:point-data"])
        self.easylist = EasyListHandler()

    def get_point_data(self, x, y):
        x -= x % 16
        y -= y % 16
        return self.point_data[y//16][x//16]
    
    def get_element_by_id(self, sg_id):
        return self.soup.find(attrs={"sg:id": sg_id})
    
    def get_element_by_point(self, x, y):
        return self.get_element_by_id(self.get_point_data(x, y))
    
    def cursor_style(self, x, y):
        elem = self.get_element_by_point(x, y)
        return elem["sg:style"]["cursor"]

    def get_bounding_box(self, elem):
        return json.loads(elem["sg:rect"])
    
    def element_aspect_ratio(self, x, y):
        elem = self.get_element_by_point(x, y)
        box = self.get_bounding_box(elem)
        while box["width"] < 15 or box["height"] < 15:
            elem = elem.parent
            box = self.get_bounding_box(elem)
        return box["width"] / box["height"], box["height"] / box["width"]
    
    def is_img(self, x, y):
        elem = self.get_element_by_point(x, y)
        return elem.name == 'img'
    
    def is_iframe(self, x, y):
        elem = self.get_element_by_point(x, y)
        return elem.name == 'iframe'
    
    def num_nested_a_tags(self, x, y):
        elem = self.get_element_by_point(x, y)
        count = 0
        while elem.parent is not None:
            if elem.name == 'a':
                count += 1
            elem = elem.parent
        return count
    
    def has_harmful_url_segment(self, x, y):
        elem = self.get_element_by_point(x, y)
        while elem.parent is not None:
            if elem.name == 'a' and "href" in elem:
                if self.easylist.is_harmful_url(elem["href"]):
                    return True
            elif elem.name in ['img', 'iframe'] and "src" in elem:
                if self.easylist.is_harmful_url(elem["src"]):
                    return True
            elem = elem.parent
        return False
    
    def text_with_styles(self, elem):
        if type(elem) == NavigableString and len(str(elem).strip()) > 0 and \
           elem.parent.name in "h1 h2 h3 h4 h5 h6 p span div":
            return [(json.loads(elem.parent["sg:style"]), str(elem))]
        ret = []
        for child in elem.children:
            try:
                ret += self.text_with_styles(child)
            except Exception:
                continue
        return ret

    @staticmethod
    def z_score_of(value_and_amount):
        total = sum(amount for value, amount in value_and_amount)
        mean = sum(value * amount for value, amount in value_and_amount) / total
        var = sum((value - mean)**2 * amount for value, amount in value_and_amount) / total
        def z(x):
            return (x - mean) / var ** 0.5
        return z

    def salient_keywords(self):
        text_and_styles = self.text_with_styles(self.soup.body)
        word_to_weight = defaultdict(lambda:{"size":0, "weight": 0})
        font_sizes = defaultdict(lambda:0)
        font_weights = defaultdict(lambda:0)
        for style, text in text_and_styles:
            for word in text.split(): #TODO NLP
                font_sizes[float(style["font-size"].replace("px", ""))] += len(word)
                font_weights[float(style["font-weight"])] += len(word)
                word_to_weight[word]["size"] = float(style["font-size"].replace("px",""))
                word_to_weight[word]["weight"] = float(style["font-weight"])

        z_size = self.z_score_of(font_sizes.items())
        z_weight = self.z_score_of(font_weights.items())

        word_to_score = defaultdict(lambda:0)
        for word, weights in word_to_weight.items():
            word_to_score[word] = max(
                word_to_score[word], 
                max(z_size(weights["size"]), 0) + 0.1 * max(z_size(weights["weight"]), 0)
            )
        
        return [word for word, score in sorted(word_to_score.items(), key=lambda x:-x[1])[:4]]

    """
    def has_harmful_css_class(self, x, y):
        elem = self.get_element_by_point(x, y)
        while elem.parent is not None:
            if "class" in elem and self.easylist.is_harmful_css_classes(elem["class"]):
                return True
            elem = elem.parent
        return False

    def has_harmful_css_id(self, x, y):
        elem = self.get_element_by_point(x, y)
        while elem.parent is not None:
            if "id" in elem and self.easylist.is_harmful_css_id(elem["id"]):
                return True
            elem = elem.parent
        return False
    """

if __name__ == "__main__":
    dom = DOMFeatureExtracter("raw_data/2.txt")
    x, y = (873, 2627)
    print(dom.get_element_by_point(x,y))
    print(dom.cursor_style(x, y))
    print(dom.element_aspect_ratio(x, y))
    print(dom.is_img(x, y))
    print(dom.is_iframe(x, y))
    print(dom.num_nested_a_tags(x, y))
    print(dom.has_harmful_url_segment(x, y))