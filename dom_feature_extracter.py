import json

from bs4 import BeautifulSoup

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
        return self.soup.find_all(attrs={"sg:id": sg_id})[0]
    
    def get_element_by_point(self, x, y):
        return self.get_element_by_id(self.get_point_data(x, y)[0])

    def cursor_style(self, x, y):
        return self.get_point_data(x, y)[1]

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