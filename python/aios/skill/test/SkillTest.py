import unittest
from dataclasses import dataclass


class SkillTest(unittest.TestCase):

    # noinspection PyMethodMayBeStatic
    def get_skill(self, props: dict = None) -> 'SkillRef':
        props = {} if props is None else props

        # TODO:
        # parse skill.yml
        # validate skill.yml
        # return SkillRef

        return None


@dataclass
class SkillRef:
    context: dict

    def evaluate(self, payload: dict):
        # TODO: delegate to skill evaluate(payload, context)
        pass

    def on_started(self):
        # TODO: delegate to skill on_started(context)
        pass

    def on_stopped(self):
        # TODO: delegate to skill on_stopped(context)
        pass
