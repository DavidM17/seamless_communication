import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '/app/src'))

import torchaudio
from helpers import publish
import logging
import torch
import boto3
import json
#from dotenv import load_dotenv

#load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRECT_ACCESS_KEY = os.getenv('AWS_SECRECT_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')
ENDPOINT_URL = os.getenv('ENDPOINT_URL')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s -- %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

resample_rate = 16000
absolute_path = os.path.dirname(__file__)

s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRECT_ACCESS_KEY, region_name=REGION_NAME,endpoint_url=ENDPOINT_URL)

def resample(audio_name):
    logger.info(f"Start resample of file: {audio_name}")
    
    waveform, sample_rate = torchaudio.load(os.path.join(absolute_path, f'../audios/{audio_name}'))
    resampler = torchaudio.transforms.Resample(sample_rate, resample_rate, dtype=waveform.dtype)
    resampled_waveform = resampler(waveform)
    
    return resampled_waveform

def download_file(body):
    data = json.loads(body.decode("utf-8").replace("'",'"'))
    key = data['file']['key']

    logger.info(f'Start download of file with key: {key}')
    
    s3.download_file(
        Filename=os.path.join(absolute_path, f'../audios/{key}'), 
        Bucket="assets-uploaded-ml", 
        Key=key
    )
    
    logger.info(f"Downloaded file with key: {key}")

def upload_file(file_name, key):
    s3.upload_file(file_name, 'assets-converted-ml', key)
    logger.info(f"File converted uploaded with key: {key}")

def evaluate(body):
    data = json.loads(body.decode("utf-8").replace("'",'"'))
    audio_name = data['file']['key']

    download_file(body)
    wave = resample(audio_name)
    
    output_path = os.path.join(absolute_path, f'../output/{audio_name}')
    tgt_lang = data['file']['tgt_lang']

    use_model(wave=wave, tgt_lang=tgt_lang, output_path=output_path)

    upload_file(output_path, audio_name)
    
    event = {
        'success': True,
        'key': audio_name,
        'tgt_lang': tgt_lang
    }
    
    publish.add(event)
    
    # files = os.listdir(os.path.join(absolute_path, '../audios'))
    # for file in files:
    #     # Pending remove from output folder
    #     if Path(file).name in [f'{audio_name}.wav', f'{audio_name}_16.wav']:
    #         os.remove(os.path.join(absolute_path, f'../audios/{file}'))
    

def use_model(wave, tgt_lang, output_path):
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        dtype = torch.float16
        logger.info(f"Running inference on the GPU in {dtype}.")
    else:
        device = torch.device("cpu")
        dtype = torch.float32
        logger.info(f"Running inference on the CPU in {dtype}.")

    s2st_model = torch.jit.load("unity_on_device.ptl")
    with torch.no_grad():
        translated_text, units, wav = s2st_model(wave, tgt_lang=tgt_lang)
    # translator = Translator('seamlessM4T_medium', 'vocoder_36langs', device, dtype)
    # translated_text, wav, sr = translator.predict(
    #     input_path,
    #     'S2ST',
    #     tgt_lang,
    #     src_lang=None,
    #     ngram_filtering=False,
    # )

        # if wav is not None and sr is not None:
        logger.info(f"Saving translated audio in {tgt_lang}")
        
        torchaudio.save(
            output_path,
            wav.unsqueeze(0),
            sample_rate=16000,
        )
        logger.info(f"Translated text in {tgt_lang}: {translated_text}")