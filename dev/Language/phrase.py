import codecs
import json
import os
import sys

import django
import pypinyin

sys.path.extend(['../..'])

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tools.settings")
django.setup()

from Model.Language.Phrase.models import Phrase, Tag, TagMap, Group, GroupSet, GroupSetMember
from Service.Language.phrase import phraseService


class PhraseLoader:
    @staticmethod
    def load_phrase():
        with codecs.open('phrase', 'r', encoding='utf8') as f:
            phrases = f.readlines()
            phrases = list(map(lambda x: x[:-1], phrases))

        for phrase in phrases:
            Phrase.new(phrase)

    @staticmethod
    def add_single_heteronym():
        phrases = Phrase.objects.all()
        for phrase in phrases:
            if len(phrase.cy) == 1:
                pys = pypinyin.pinyin(phrase.cy, heteronym=True)[0]
                current_py = json.loads(phrase.py)[0]
                for py in pys:
                    if py != current_py:
                        Phrase.new(phrase.cy, [py])

    @staticmethod
    def set_number_py():
        phrases = Phrase.objects.filter(number_py='')
        for phrase in phrases:
            pys = json.loads(phrase.py)
            for index, py in enumerate(pys):
                pys[index] = phraseService.format_syllable(py, printer='number_toner')
            pys = json.dumps(pys, ensure_ascii=False)
            phrase.number_py = pys
            phrase.save()


PhraseLoader.set_number_py()
