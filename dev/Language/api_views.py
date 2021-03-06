import json

from SmartDjango import Analyse, BaseError, P, E
from SmartDjango.models import Pager
from django.views import View

from Base.param_limit import PL
from Model.Base.Config.models import Config
from Model.Language.Phrase.models import Tag, TagMap, Phrase
from Service.Language.phrase import phraseService


PM_TAG_NAME = Tag.get_param('name')
PM_TAG_ID = P('tag_id', yield_name='tag').process(Tag.get_by_id)
PM_PHRASES = P('phrases').validate(list).process(
        lambda phrases: list(map(Phrase.get_by_id, phrases)))
PM_MATCHED = PM_PHRASES.clone().rename('matched')
PM_UNMATCHED = PM_PHRASES.clone().rename('unmatched')
PM_ACTION = P('action').process(str).default('add')


@E.register()
class DevLangPhraseError:
    CONTRIBUTOR_NOT_FOUND = E("贡献者不存在")


def get_contributor(entrance):
    entrance_key = 'LangPhraseEntrance'
    entrances = json.loads(Config.get_value_by_key(entrance_key))
    if entrance in entrances:
        return entrances[entrance]
    raise DevLangPhraseError.CONTRIBUTOR_NOT_FOUND


PM_ENTRANCE = P('entrance', yield_name='contributor').process(get_contributor)


class PhraseView(View):
    @staticmethod
    @Analyse.r(q=[PM_TAG_ID, P('count').process(int).process(PL.number(100, 1))])
    def get(r):
        tag = r.d.tag
        count = r.d.count

        phrases = phraseService.phrases \
            .exclude(pk__in=TagMap.objects.filter(
                tag=tag, match__isnull=False).values_list('phrase', flat=True)) \
            .order_by('pk')[:count]
        return phrases.dict(Phrase.d)

    @staticmethod
    @Analyse.r(b=['cy', PM_ENTRANCE, PM_ACTION, PM_TAG_ID.clone().null()])
    def post(r):
        cy = r.d.cy
        action = r.d.action

        if action == 'add':
            cy = Phrase.new(cy)
            contributor = r.d.contributor
            add_key = 'LangPhraseAdd-' + contributor
            add_count = int(Config.get_value_by_key(add_key, 0))
            Config.update_value(add_key, str(add_count + 1))
            return cy.d()
        else:
            if not r.d.tag:
                return BaseError.MISS_PARAM(('tag_id', '标签'))
            tag = r.d.tag
            cy = Phrase.get(cy)
            tagmap = TagMap.get(cy, tag)
            return tagmap.d()

    @staticmethod
    @Analyse.r(b=[PM_TAG_ID, PM_MATCHED, PM_UNMATCHED, PM_ENTRANCE])
    def put(r):
        tag = r.d.tag
        contributor = r.d.contributor

        contributor_key = 'LangPhraseContributor-' + contributor
        contribute_page = int(Config.get_value_by_key(contributor_key, 0))
        Config.update_value(contributor_key, str(contribute_page+1))

        for phrase in r.d.matched:
            TagMap.new_or_put(phrase, tag, match=True)
        for phrase in r.d.unmatched:
            TagMap.new_or_put(phrase, tag, match=False)


class TagView(View):
    @staticmethod
    def get(r):
        return Tag.objects.dict(Tag.d)

    @staticmethod
    @Analyse.r(b=[PM_TAG_NAME])
    def post(r):
        name = r.d.name
        Tag.new(name)

    @staticmethod
    @Analyse.r(b=[PM_TAG_NAME], q=[PM_TAG_ID])
    def put(r):
        tag = r.d.tag
        name = r.d.name
        tag.put(name)

    @staticmethod
    @Analyse.r(q=[PM_TAG_ID])
    def delete(r):
        tag = r.d.tag
        tag.remove()


class ContributorView(View):
    @staticmethod
    @Analyse.r(b=[PM_ENTRANCE])
    def post(r):
        contributor = r.d.contributor
        contributor_key = 'LangPhraseContributor-' + contributor
        contribute_page = int(Config.get_value_by_key(contributor_key, 0))
        add_key = 'LangPhraseAdd-' + contributor
        add_count = int(Config.get_value_by_key(add_key, 0))

        return dict(contribute_page=contribute_page, add_count=add_count, contributor=contributor)


class ReviewView(View):
    @staticmethod
    @Analyse.r(q=[
        PM_TAG_ID,
        P('count').process(int).process(PL.number(100, 1)),
        P('last').process(int)
    ])
    def get(r):
        tag = r.d.tag
        last = r.d.last
        count = r.d.count

        objects = TagMap.objects.search(tag=tag)
        return Pager().page(objects, last, count).dict(TagMap.d)
