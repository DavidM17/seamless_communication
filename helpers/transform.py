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

def resample(audio_name):
    waveform, sample_rate = torchaudio.load(f'/content/seamless_communication/audios/{audio_name}.wav')
    resampler = torchaudio.transforms.Resample(sample_rate, resample_rate, dtype=waveform.dtype)
    resampled_waveform = resampler(waveform)
    torchaudio.save(f'audios/{audio_name}_16.wav', resampled_waveform, resample_rate)

def test(body):
    publish.add(body)

def use_model(args):
    device = torch.device("cpu")
    dtype = torch.float32
    logger.info(f"Running inference on the CPU in {dtype}.")

    translator = Translator('seamlessM4T_medium', 'vocoder_36langs', device, dtype)
    translated_text, wav, sr = translator.predict(
        args.input_path,
        'S2ST',
        args.tgt_lang,
        src_lang=None,
        ngram_filtering=False,
    )

    if wav is not None and sr is not None:
        logger.info(f"Saving translated audio in {args.tgt_lang}")
        torchaudio.save(
            args.output_path,
            wav[0].to(torch.float32).cpu(),
            sample_rate=sr,
        )
    logger.info(f"Translated text in {args.tgt_lang}: {translated_text}")