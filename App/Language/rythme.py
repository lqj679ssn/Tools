from SmartDjango import Analyse, P
from smartify import PDict

from Base.handler import BaseHandler
from Base.param_limit import PL
from Base.router import Router
from Service.Language.phrase import Syllables, SyllableClusters


class Rythme(BaseHandler):
    class RythmeCluster(BaseHandler):
        APP_NAME = '押韵拼音组'
        APP_DESC = 'cluster和cluster_type的取值说明。\n' \
                   '通过POST请求获取音节(syllable)数据。\n' \
                   'syllables分为22个组，每组的音节视为互可押韵。\n' \
                   'cluster_type参数可以是strict, normal, custom。\n' \
                   '当其为strict时，此22组相互独立。组内相互押韵，组间不为押韵；\n' \
                   '当其为normal时，以下组间相互押韵：%s；\n' \
                   '当其为custom时，cluster表示自定义组间押韵，格式与normal的例子相同' % \
                   ', '.join(map(str, SyllableClusters['normal']))

        @staticmethod
        def run(r):
            return dict(syllables=Syllables)

    APP_NAME = '押韵'
    APP_DESC = '查找和目标押韵（支持二押及以上）的词语'

    BODY = [
        P('py', '拼音').validate(list),
        PDict(name='phrase', read_name='目标词语长度限制').null().set_fields(
            P('max', '词语最大长度').null(), P('min', '词语最小长度').null()),
        PDict(name='rythme', read_name='目标词语押韵限制').null().set_fields(
            P('max', '词语最长押韵数').null(), P('min', '词语最短押韵数').null()),
        P('cluster', '押韵拼音组').null(),
        P('cluster_type', '押韵拼音组模式')
            .default('normal').process(PL.choices(SyllableClusters)),
    ]

    SUB_ROUTER = Router()
    SUB_ROUTER.register_param('cluster', RythmeCluster)

    @staticmethod
    @Analyse.r(b=BODY)
    def run(r):
        py = r.d.py
        phrase_limit = r.d.phrase or dict(max=None, min=None)
        rythme_limit = r.d.rythme or dict(max=None, min=None)
        cluster = r.d.cluster
        cluster_type = r.d.cluster_type

