from python.aios.skill.exceptions.SkillYamlParseError import SkillYamlParseError


class SkillYamlInvalidValueError(SkillYamlParseError):

    def __init__(self, key, path):
        super().__init__("Invalid value for key '{}' in {}".format(key, path))
