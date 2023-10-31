import os
from pathlib import Path
import torchaudio
from helpers import publish
import logging
import torch
import torchaudio
from seamless_communication.models.inference import Translator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s -- %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

resample_rate = 16000
absolute_path = os.path.dirname(__file__)

def resample(audio_name):
    waveform, sample_rate = torchaudio.load(os.path.join(absolute_path, f'../audios/{audio_name}.wav'))
    resampler = torchaudio.transforms.Resample(sample_rate, resample_rate, dtype=waveform.dtype)
    resampled_waveform = resampler(waveform)
    torchaudio.save(os.path.join(absolute_path, f'../audios/{audio_name}_16.wav'), resampled_waveform, resample_rate)

def download_file():
    print('Download from s3')

def upload_file():
    print('Upload to s3')

def evaluate(body):
    # download_file(body)

    resample(body['audio_name'])
    audio_name = body['audio_name']

    input_path = os.path.join(absolute_path, f'../audios/{audio_name}_16.wav')
    output_path = os.path.join(absolute_path, f'../output/{audio_name}.wav')
    tgt_lang = body['tgt_lang']

    use_model(input_path=input_path, tgt_lang=tgt_lang, output_path=output_path)

    # upload_file(body)
    # publish.add(body)
    
    files = os.listdir(os.path.join(absolute_path, '../audios'))
    for file in files:
        # Pending remove from output folder
        if Path(file).name in [f'{audio_name}.wav', f'{audio_name}_16.wav']:
            os.remove(os.path.join(absolute_path, f'../audios/{file}'))
    

def use_model(input_path, tgt_lang, output_path):
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        dtype = torch.float16
        logger.info(f"Running inference on the GPU in {dtype}.")
    else:
        device = torch.device("cpu")
        dtype = torch.float32
        logger.info(f"Running inference on the CPU in {dtype}.")

    translator = Translator('seamlessM4T_medium', 'vocoder_36langs', device, dtype)
    translated_text, wav, sr = translator.predict(
        input_path,
        'S2ST',
        tgt_lang,
        src_lang=None,
        ngram_filtering=False,
    )

    if wav is not None and sr is not None:
        logger.info(f"Saving translated audio in {tgt_lang}")
        torchaudio.save(
            output_path,
            wav[0].to(torch.float32).cpu(),
            sample_rate=sr,
        )
    logger.info(f"Translated text in {tgt_lang}: {translated_text}")