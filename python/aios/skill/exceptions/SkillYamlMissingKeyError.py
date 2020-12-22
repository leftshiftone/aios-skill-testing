from python.aios.skill.exceptions.SkillYamlParseError import SkillYamlParseError


class SkillYamlMissingKeyError(SkillYamlParseError):

    def __init__(self, key, path):
        super().__init__("Missing mandatory key '{}' in {}".format(key, path))
