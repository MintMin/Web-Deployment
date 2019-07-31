import aiohttp
import asyncio
import uvicorn
import os
from fastai import *
from fastai.vision import *
import random
import string
from io import BytesIO
from io import StringIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from google.cloud import storage
from PIL import Image
import pandas as pd

# implement our model here 
export_file_url = 'https://www.dropbox.com/s/yuwyshs6tmwp46b/trained_model_1%20%281%29.pkl?raw=1'
export_file_name = 'export.pkl'

#list trash categories here 
classes = ['Cardboard', 'E-Waste', 'Glass', 'Metal', 'Paper', 'Plastic', 'Trash']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

# define the root path
@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


# define the analyze button action    
@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await (img_data['file'].read())
    img = open_image(BytesIO(img_bytes))
    prediction = str(learn.predict(img)[0])
    print(prediction)
    if(prediction != 'Trash' and prediction != 'E-Waste'):
        prediction = 'Recyclable (' + prediction + ')'
    return JSONResponse({'result': prediction})

# define the submit action    
# specify the saving location of submitted images
@app.route('/submit', methods=['POST'])
async def submit(request):
    img_data = (await request.form())
    for key in img_data.keys():
        pred = key
        start = 'F'
        d = 0
        print(pred, '==', img_data['pre'])
        if(pred == img_data['pre']):
            start = 'T'
            d = 1
        break
    img_bytes = await (img_data[pred].read())
    img = open_image(BytesIO(img_bytes))
    prediction = pred
    # bucket upload...
    # """Uploads a file to the bucket."""
    export_file = 'https://www.dropbox.com/s/71k0wvn42a4y5h3/engaged-cosine-245518-8280e6195129.json?raw=1'
    await download_file(export_file, path / 'JSON.json')
    storage_client = storage.Client.from_service_account_json(
        'app/JSON.json')
    buckets = list(storage_client.list_buckets())
    bucket = storage_client.get_bucket('amli_trashnet_photos')
    alias = start
    alias = alias + ''.join(random.choice(string.ascii_letters) for _ in range(32))
    # GStorage  
    print(alias, 'to', prediction)
    if(prediction[0] == ' '):
        prediction = prediction[1:]
    blobstr = 'Web_data/' + prediction + '/' + alias
    csvobject = 'Web_data/Web_App_DB.csv'
    csvblob = bucket.blob(csvobject)
    # df = pd.read_csv('gs://Web_data/Web_App_DB.csv',encoding='utf-8')
    a = csvblob.download_as_string()
    df = pd.read_csv(BytesIO(a))
    blob = bucket.blob(blobstr)
    blob.upload_from_string(img_bytes, content_type = 'image/jpeg')
    #make new row for df
    link = 'https://storage.cloud.google.com/amli_trashnet_photos/Web_data/'+ prediction + '/' + alias + '?folder=true&organizationId=765589025310'
    row = [link, img_data['pre'], prediction, str(d)]
    df2 = pd.DataFrame([row], columns=df.columns)
    df.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)
    df = df.append(df2)
    newcsv = df.to_csv(index = False)
    csvblob.upload_from_string(newcsv)
    
    return JSONResponse({'result': str(prediction)})

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
