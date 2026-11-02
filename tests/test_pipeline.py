import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from darkstudio.cli import split_text, load_config
from darkstudio.story import make_story, validate_story
from darkstudio.media import captions, timestamp, verify
from darkstudio.images import comfy_image


class PipelineTests(unittest.TestCase):
    def test_full_story_has_target_word_range_and_repeatable_seed(self):
        story=validate_story(make_story(42),True)
        self.assertEqual(story,make_story(42))
        self.assertNotEqual(story,make_story(97))
        self.assertEqual(len(story['scenes']),12)

    def test_bad_story_rejected(self):
        for story in ({}, {'title':'abc','scenes':[]}, {'title':'abc','scenes':[{'text':'a','visual':'x'}]}):
            with self.assertRaises(ValueError): validate_story(story)
        with self.assertRaises(ValueError): validate_story(make_story(42,True),True)

    def test_chunking_preserves_words_and_punctuation(self):
        text='A porta abriu. '+ ' '.join(['silêncio']*40)+'.'
        chunks=split_text(text)
        self.assertEqual(' '.join(chunks),text)
        self.assertTrue(all(len(c.split())<=18 for c in chunks))

    def test_subtitles_have_measured_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'captions.srt'
            seconds=captions([{'text':'Primeira frase.','duration':1.25},{'text':'Segunda frase.','duration':2.75}],target)
            self.assertEqual(seconds,4)
            self.assertIn('00:00:01,250 --> 00:00:04,000',target.read_text())
        self.assertEqual(timestamp(3600.001),'01:00:00,001')

    def test_duration_and_dimensions_quality_gate(self):
        info={'streams':[{'codec_type':'video','width':1080,'height':1920,'codec_name':'h264'},{'codec_type':'audio','codec_name':'aac'}],'format':{'duration':'61'}}
        with patch('darkstudio.media.probe',return_value=info),patch('darkstudio.media.run'):
            with self.assertRaises(ValueError):verify('unused',{'ffmpeg':'ffmpeg'},1080,1920,61,True)
            info['format']['duration']='45'
            self.assertTrue(verify('unused',{'ffmpeg':'ffmpeg'},1080,1920,45,True)['passed'])
            with self.assertRaises(ValueError):verify('unused',{'ffmpeg':'ffmpeg'},1920,1080,45)

    def test_free_local_only_comfyui(self):
        with self.assertRaises(ValueError):comfy_image('test',Path('unused'),{'comfyui_url':'https://paid.example.com'})

    def test_configuration_guards(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'config.json';f.write_text(json.dumps({'speech_rate':500}))
            with self.assertRaises(ValueError):load_config(f)


if __name__=='__main__':unittest.main()
