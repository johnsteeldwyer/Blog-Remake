from bs4 import BeautifulSoup
import json
import os
import requests
import shutil

PICS_PATH = "your/pic/path"

with open(file="blog.html", encoding="UTF-8", mode="r") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")

    # Find dates
    days = soup.find_all(class_="date_day")
    months = soup.find_all(class_="date_month")
    years = soup.find_all(class_="date_year")
    dates = []
    for i, day in enumerate(days):
        dates.append(f"{days[i].text}-{months[i].text}-{years[i].text}")

    # Titles
    titles = soup.select("h2 a")
    for i, title in enumerate(titles):
        titles[i] = titles[i].text
        if titles[i][-1] == " ":
            titles[i] = titles[i][:-1]

    # Categories
    smalls = soup.find_all(name="small")
    categories = []
    for small in smalls:
        if "Categories : " in small.text:
            categories_nonlist = small.text.split(": ")[1]
            categories_listed = categories_nonlist.split(", ")
            categories.append(categories_listed)

    # Content
    posts = soup.find_all("div", attrs={"class": "entry"})
    content = []
    subtitles = []
    captions = []
    for i, post in enumerate(posts):

        # Imgs and Captions
        img_figs = post.find_all('figure')
        img_captions = []
        
        img_figs = post.find_all('figure')
        img_captions = []
        
        # Combine img links and captions
        for k, fig in enumerate(img_figs):
            try:
                img = fig.find("img")["data-orig-file"]
            except:
                img = fig.find("img")["src"]
            try:
                caption = fig.find("figcaption").text
            except AttributeError:
                caption = None
            img_captions.append(caption)
        captions.append(img_captions)
        
        try:
            os.mkdir(f"{PICS_PATH}/post{i}")
        except:
            shutil.rmtree(f"{PICS_PATH}/post{i}")	
            os.mkdir(f"{PICS_PATH}/post{i}")
        
        for j, img in enumerate(images):
            r = requests.get(img[f'img_{j}']['img_link']).content
            with open(f"{PICS_PATH}/post{i}/post{i}pic{j}.jpg","wb+") as f:
                f.write(r)

        # Text and Subs
        ps = []
        sections = post.find_all("p")
        if len(sections[0].text) > 100:
            sub = sections[0].text[:100] + "..."
            subtitles.append(sub)
            ps.append(sections[0].text)
        else:
            subtitles.append(sections[0].text)
        for i in range(1, len(sections)):
            ps.append(sections[i].text)
        content.append(ps)
    
# Create Posts
blog_posts = []
for i, title in enumerate(titles):
    blog_posts.append(
        {
            "num": i,
            "date": dates[i],
            "title": titles[i],
            "subtitle": subtitles[i],
            "categories": categories[i],
            "content": content[i],
            "captions": captions[i]
        }
    )
    
blog_posts_json = (json.dumps(blog_posts))
with open(file="posts.txt", encoding="utf-8", mode="w") as file:
    file.write(blog_posts_json)
    
