# json COCO TLDR

REFERENCE: https://auto.gluon.ai/dev/tutorials/multimodal/object_detection/data_preparation/convert_data_to_coco_format.html

# How to prepare COCO format
## 1.Formatting folder Structure
Under the COCO format, the overall folder structure of a dataset should follow:

```xml
<dataset_dir>/
    images/
        <imagename0>.<ext>
        <imagename1>.<ext>
        <imagename2>.<ext>
        ...
    annotations/
        train_labels.json
        val_labels.json
        test_labels.json
        ...
```


## 2. Formatting *_labels.json
Below are the key names and value definitions inside *_labels.json:

```json
{
    "info": info,
    "licenses": [license], 
    "images": [image],  // list of all images in the dataset
    "annotations": [annotation],  // list of all annotations in the dataset
    "categories": [category]  // list of all categories
}
```
where:
```json
info = {
    "year": int, 
    "version": str, 
    "description": str, 
    "contributor": str, 
    "url": str, 
    "date_created": datetime,
}

license = {
    "id": int, 
    "name": str, 
    "url": str,
}

image = {
    "id": int, 
    "width": int, 
    "height": int, 
    "file_name": str, 
    "license": int,  // the id of the license
    "date_captured": datetime,
}

category = {
    "id": int, 
    "name": str, 
    "supercategory": str,
}

annotation = {
    "id": int, 
    "image_id": int,  // the id of the image that the annotation belongs to
    "category_id": int,  // the id of the category that the annotation belongs to
    "segmentation": RLE or [polygon], 
    "area": float, 
    "bbox": [x,y,width,height], 
    "iscrowd": int,  // 0 or 1,
}
```
For the sole purpose of running AutoMM, the fields "info" and "licenses" are optional. "images", "categories", and "annotations" are required for training and evaluation, while for prediction only the "images" field is required.
```json
{
    "info": {...},
    "licenses": [
        {
            "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/", 
            "id": 1, 
            "name": "Attribution-NonCommercial-ShareAlike License"
        },
        ...
    ],
    "categories": [
        {"supercategory": "person", "id": 1, "name": "person"},
        {"supercategory": "vehicle", "id": 2, "name": "bicycle"},
        {"supercategory": "vehicle", "id": 3, "name": "car"},
        {"supercategory": "vehicle", "id": 4, "name": "motorcycle"},
        ...
    ],
        
    "images": [
        {
            "license": 4, 
            "file_name": "<imagename0>.<ext>", 
            "height": 427, 
            "width": 640, 
            "date_captured": null, 
            "id": 397133
        },
        ...
    ],
    "annotations": [
        
        ...
    ]
}
```


---

# Context - ARbotox:

Minimum requirements for COCO json.

### `annotations` Section

Each entry in the annotations section should include:

```
id (int): unique identifier for the annotation.
image_id (int): ID of the image that this annotation belongs to, linking it to an entry in images.
category_id (int): ID of the category for this annotation, linking it to an entry in categories.
bbox (array of 4 floats/ints): bounding box coordinates in [x, y, width, height] format.
segmentation (array or RLE, optional): a list of polygons or run-length encoded data for the segmentation mask. While segmentation is technically optional, it is essential for any plotting of segmentation masks.
area (float, optional but recommended): area of the segmentation or bounding box. pycocotools calculates the area if it’s missing, but providing it can improve performance.
iscrowd (int, optional, default=0): 0 if the annotation represents an individual object, 1 if it represents a group.
```

### `categories` Section

Each entry in the categories section must contain:
```
id (int): unique identifier for each category.
name (string): name of the category e.g. "Eye Region"
supercategory (string, optional): higher-level grouping for the category e.g., "face"