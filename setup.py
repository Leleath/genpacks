import os

try:
    os.system("pip install requests") 
    os.system("pip install shutil") 
    os.system("pip install zipfile") 
    os.system("pip install pydub") 
    os.system("pip install concurrent.futures") 
    os.system("pip install PIL")  
    os.system("pip install ffmpeg-python")  
except Exception as e:
    print ('Process failed', e)