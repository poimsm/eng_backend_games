import os
import uuid
import ffmpeg
import logging

logger = logging.getLogger('audio_converter')


class AudioConverter:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.audios_dir = os.path.join(base_dir, 'audios')
        if not os.path.exists(self.audios_dir):
            os.makedirs(self.audios_dir)
            logger.info('Audio directory created at: ' + self.audios_dir)

        self.reqID = ''
        logger.info(f'ReqID={self.reqID} | AudioConverter initialized')

    def convert(self, audio_file):
        unique_id = uuid.uuid4()
        input_filename = f'{unique_id}.aac'
        output_filename = f'{unique_id}.webm'

        path_input = os.path.join(self.audios_dir, input_filename)
        path_output = os.path.join(self.audios_dir, output_filename)

        with open(path_input, 'wb+') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
        logger.info(f'ReqID={self.reqID} | Audio file saved as {input_filename}')

        logger.info( f'ReqID={self.reqID} | Starting conversion from {input_filename} to {output_filename}')
        stream = ffmpeg.input(path_input)
        audio = stream.audio
        stream = ffmpeg.output(audio, path_output, format='webm', acodec='libvorbis')
        ffmpeg.run(stream)
        logger.info(f'ReqID={self.reqID} | Conversion completed. Output file: {output_filename}')

        probe = ffmpeg.probe(path_input)
        audio_info = next(
            s for s in probe['streams'] if s['codec_type'] == 'audio')
        duration_seconds = float(audio_info['duration'])
        logger.info(f'ReqID={self.reqID} | Audio duration: {duration_seconds} seconds')

        # Optional: Remove the input file after conversion
        # os.remove(path_input)
        # logger.info(f'ReqID={self.reqID} | Input file {input_filename} removed after conversion')

        return path_output, duration_seconds
