import io
import os

# Imports the Google Cloud client library
from google.cloud import vision

from jinja2 import Template

path = "images"

os.chdir(path)

# Instantiates a client
client = vision.ImageAnnotatorClient()

categories = []

# iterate through all images
for root, directories, files in os.walk("."):

    for directory in directories:

        directory_map = {}
        directory_map["name"] = directory
        directory_map["ltks"] = []

        dirpath = "./" + directory

        for img_root, img_dirs, img_files in os.walk(dirpath):
            ltks = []
            for file_name in img_files:
                if file_name.endswith(('.jpg','.webp')):
                    ltk_name = file_name.split(".")[0]
                    ltk_id = ltk_name.split("_")[0]
                    image_id = ltk_name.split("_")[1]
                    ltk_url = "https://www.liketoknow.it/ltk/"+ltk_id
                    image_url = "https://images.liketoknow.it/"+image_id+'?auto=format&fm=webp&w=360&q=80&dpr=1'

                    with open(dirpath + "/" + file_name, 'rb') as image_file:
                        content = image_file.read()
                        image = vision.Image(content=content)
                        response = client.label_detection(image=image, max_results=20)
                        labels = response.label_annotations

                        print('Labels for : '+file_name)
                        labelscores = []
                        for label in labels:
                            if label.score > 0.7:
                                labelscores.append(label.description + ' | ' + str(round(label.score*100, 2)) + '%')
                    
                    directory_map["ltks"].append({
                        "name":ltk_name,
                        "url": ltk_url,
                        "image_url": image_url,
                        "scores": labelscores
                    })
    
        categories.append(directory_map)

#print(categories)
with open('../template.html') as file_:
    template = Template(file_.read())
rendered_file = template.render(categories=categories)

bytes = rendered_file.encode(encoding='UTF-8')

with open("../results.html", "wb") as f:
    f.write(bytes)

