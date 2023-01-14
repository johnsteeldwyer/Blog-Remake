from bs4 import BeautifulSoup
import json
import os
import requests
import shutil

PICS_PATH = "C:/Users/17722/Desktop/JDwyer/Code/100-Days-of-Code/58-blog-updated/static/assets/pics"

with open(file="gallary.html", mode="r") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")

    # Content
    content = []
    subtitles = []
    captions = []

    # Imgs and Captions
    img_figs = soup.find_all('figure')
    img_captions = []
    imgs = []
    # Combine img links and captions
    for i, fig in enumerate(img_figs):
        try:
            img = fig.find("img")["data-orig-file"]
        except:
            img = fig.find("img")["src"]
        try:
            caption = fig.find("figcaption").text
        except AttributeError:
            caption = None
        img_captions.append(caption)
        imgs.append(img)
    
img_captions = (json.dumps(img_captions))
print(img_captions)
with open(file="gallary-captions.txt", encoding="utf-8", mode="w") as file:
    file.write(img_captions)
    
try:
    os.mkdir(f"gallary")
except:
    shutil.rmtree(f"gallary")	
    os.mkdir(f"gallary")

for j, img in enumerate(imgs):
    r = requests.get(img).content
    with open(f"gallary/pic{j}.jpg","wb+") as f:
        f.write(r)
    
