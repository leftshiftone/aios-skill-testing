import unittest
from python.aios.skill.test.SkillTest import SkillTest
import pathlib
import os


class SomeTest(SkillTest):
    """ This test shows the simplest setup to run a basic skill unit test. """

    def setUp(self) -> None:
        self.skill_config_path = os.path.join(pathlib.Path().absolute(), 'skill.yml')
        self.contract_path = os.path.join(pathlib.Path().absolute(), 'contract.dbs')
        self.handler_path = 'python.test.handler'

    def test_evaluate(self):
        skill_ref = SkillTest.get_skill(skill_config_path=self.skill_config_path,
                                        contract_path=self.contract_path,
                                        handler_path=self.handler_path,
                                        provision_parameter={"ACTIVATE_SCORES": "activate"})
        skill_ref.evaluate({"data": "test"})

    @unittest.skip(reason="testing validation")
    def test_on_started(self):
        skill_ref = SkillTest.get_skill(skill_config_path=self.skill_config_path,
                                        contract_path=self.contract_path,
                                        handler_path=self.handler_path)
        skill_ref.on_started()

    @unittest.skip(reason="testing validation")
    def test_on_stopped(self):
        skill_ref = SkillTest.get_skill(skill_config_path=self.skill_config_path,
                                        contract_path=self.contract_path,
                                        handler_path=self.handler_path)
        skill_ref.on_stopped()


if __name__ == '__main__':
    unittest.main()
