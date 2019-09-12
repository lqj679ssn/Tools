import pypinyin
from SmartDjango import Excp, Param, Analyse

from Base.handler import BaseHandler
from Base.param_limit import PL


class CharacterToPinyin(BaseHandler):
    APP_NAME = '汉字转拼音'
    APP_DESC = '支持多音字判别，拼音自带音调'

    BODY = [Param('text', '汉字').validate(PL.str_len(500))]
    REQUEST_EXAMPLE = {'text': '林俊杰'}
    RESPONSE_EXAMPLE = ["lín", "jùn", "jié"]

    @staticmethod
    @Excp.handle
    @Analyse.r(b=BODY)
    def run(r):
        text = r.d.text
        pinyin = pypinyin.pinyin(text, errors=lambda _: [None])
        return list(map(lambda x: x[0], pinyin))
