# From-Web-To-Patch
It deals with every procedure required to convert a website into a CNN-feedable patches.

## Web to Local Data

### screenshot

* Use the Chrome browser with "Full Page Screen Capture" extention
* Make sure that your browser is scaled to 100% (press ctrl and +/- to check)
* Paste and save the file as `raw_data/[id].png`

### DOM data

* Copy `augment_dom.js` and paste at console of Chrome developer tool
* Press "copy" button at the console result (or right click at the topmost HTML element in "elements" tab and click "Copy > Copy element")
* Paste and save the file as `raw_data/[id].html`

*Note* Inner contents iframes are not captured. Only the topmost iframe will present in the result.

## Local Data to Patch

See the example below.

```python
from patch_manager import PatchManager
pm = PatchManager()
pm.feed(['raw_data/0.png', 'raw_data/0.html'])
pm.feed(['raw_data/1.png', 'raw_data/1.html'])
pm.save_patches_at('patches/') # root directory where the patches are
with open('spec.json', 'w') as f:
    f.write(pm.generate_spec())
```
It will generate the `spec.json` file with the template

```json
{
    "width": 96, // patch_width
    "height": 96, // patch_height
    "root": "patches/", // root directory where the patches are
    "tags": [
        {"name": "text"}, ...
    ], // labels
    "data": [
        {
            "id": 0, // data id
            "filename": "0.png", // the whole image will be at "images/0/0.png"
            "width": 1120, "height": 1700, // width and height of the whole image
            "patches": [
                {
                    "filename": "0x0.png", // this patch will be at "images/0/0x0.png"
                    "left": 0, "right": 127, "top": 0, "bottom": 127, // position of the patch w.r.t. the entire image (inclusive)
                    "tags": [ 0, 0.3, 0.2, ... ], // proportion of the tags
                    "features": {
                        "cursor": "pointer",
                        "nested_a": 1,
                        "is_img": true,
                        "is_iframe": true,
                        "contains_harmful_url": true, 
                    }
                }
            ]

        }
    ]
}
```