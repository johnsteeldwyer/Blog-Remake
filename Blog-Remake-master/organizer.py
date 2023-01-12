import shutil
import os

counter = 30
for i in range(0,31):
    os.mkdir(f'static/assets/pictures/post{counter}')
    for j in range(10):
        try:
            shutil.copyfile(f'static/assets/pics/post{i}/post{i}pic{j}.jpg', f'static/assets/pictures/post{counter}/pic{j}.jpg')
        except:
            break
    counter -= 1
