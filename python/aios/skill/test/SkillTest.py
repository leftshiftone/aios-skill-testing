import os
import unittest
import yaml
import validators
import re
import pathlib

from python.aios.skill.exceptions.SkillYamlInvalidValueError import SkillYamlInvalidValueError
from python.aios.skill.exceptions.SkillYamlMissingKeyError import SkillYamlMissingKeyError
from python.aios.skill.test.SkillRef import SkillRef


class SkillTest(unittest.TestCase):

    @staticmethod
    def get_skill(provision_parameter: dict = None, skill_config_path: str = None, contract_path: str = None, handler_path: str = None) -> SkillRef:
        """
        :param provision_parameter: add skill provision parameters here to simulate runtime behaviour
        :param skill_config_path: path to skill configuration file (skill.yml); only necessary if the configuration file deviates from the conventions
        :param contract_path: path to dynabuffers skill contract (*.dbs); only necessary if the contract file deviates from the conventions; if parameter is not provided the first contract
        found in skill.yml is used
        :param handler_path: path to python handler module (i.e. starting point of skill); only necessary if the python module is located at another place other than the convention (which is
        directly below the root folder 'src')
        :return:
        """

        provision_parameter = SkillTest.get_provision_parameter(provision_parameter)
        skill_config_path = SkillTest.get_skill_config_path(skill_config_path)
        evaluate_function, module_name, contract = SkillTest.parse_skill_config(skill_config_path)
        contract_path = SkillTest.get_contract_path(contract, contract_path)
        SkillTest.make_provision_params_available_in_env(provision_parameter)

        return SkillRef(context=provision_parameter, handler_module=module_name, evaluate_function=evaluate_function, handler_path=handler_path, contract_path=contract_path)

    @staticmethod
    def get_contract_path(contract: str, contract_path: str):
        if contract_path is None:
            current_dir = pathlib.Path().absolute()
            contract_path = os.path.join(current_dir.parent, 'contract/contract.dbs')
        return contract_path

    @staticmethod
    def get_provision_parameter(provision_parameter):
        provision_parameter = {} if provision_parameter is None else provision_parameter
        return provision_parameter

    @staticmethod
    def parse_skill_config(skill_config_path):
        with open(skill_config_path) as f:
            skill_config = yaml.load(f, Loader=yaml.FullLoader)
            SkillTest.validate_skill_identifier(skill_config, skill_config_path)
            SkillTest.validate_version_control(skill_config, skill_config_path)
            SkillTest.validate_skill_license(skill_config, skill_config_path)
            SkillTest.validate_additional_properties(skill_config, skill_config_path)
            SkillTest.validate_image(skill_config, skill_config_path)

            properties = "properties"
            if properties not in skill_config.keys():
                raise SkillYamlMissingKeyError(properties, skill_config_path)
            if skill_config[properties] and len(skill_config[properties]) > 0:
                for property in skill_config[properties]:
                    if not property:
                        raise SkillYamlInvalidValueError(properties + ": " + property, skill_config_path)
                    for key in property.keys():
                        if key not in ['name', 'desc', 'default', 'pattern']:
                            raise SkillYamlInvalidValueError(properties + ": " + property + ": " + key, skill_config_path)

            SkillTest.validate_contract(skill_config, skill_config_path)
            SkillTest.validate_composable(skill_config, skill_config_path)
            SkillTest.validate_network_access(skill_config, skill_config_path)
            SkillTest.validate_resources(skill_config, skill_config_path)
            SkillTest.validate_permissions(skill_config, skill_config_path)
            SkillTest.validate_skill_handler(skill_config, skill_config_path)

            module_name = skill_config['handler']['file']
            evaluate_function = skill_config['handler']['function']
            contract = skill_config['contract'][0]

        return evaluate_function, module_name, contract

    @staticmethod
    def validate_composable(skill_config, skill_config_path):
        composable = 'composable'
        if composable not in skill_config.keys():
            raise SkillYamlMissingKeyError(composable, skill_config_path)
        if not str(skill_config[composable]) or str(skill_config[composable]).lower() not in ['true', 'false']:
            raise SkillYamlInvalidValueError(composable, skill_config_path)

    @staticmethod
    def validate_network_access(skill_config, skill_config_path):
        network_access = 'network_access'
        if network_access not in skill_config.keys():
            raise SkillYamlMissingKeyError(network_access, skill_config_path)
        if not str(skill_config[network_access]) or str(skill_config[network_access]).lower() not in ['true', 'false']:
            raise SkillYamlInvalidValueError(network_access, skill_config_path)

    @staticmethod
    def validate_contract(skill_config, skill_config_path):
        contract = "contract"
        if contract not in skill_config.keys():
            raise SkillYamlMissingKeyError(contract, skill_config_path)
        if skill_config[contract] is None or len(skill_config[contract]) < 1:
            raise SkillYamlInvalidValueError(contract, skill_config_path)
        for label in skill_config[contract]:
            if not label:
                raise SkillYamlInvalidValueError(contract, skill_config_path)

    @staticmethod
    def validate_resources(skill_config, skill_config_path):
        resources = "resources"
        if resources not in skill_config.keys():
            raise SkillYamlMissingKeyError(resources, skill_config_path)

        SkillTest.validate_cpu(skill_config, skill_config_path, resources)
        SkillTest.validate_memory(skill_config, skill_config_path, resources)

    @staticmethod
    def validate_cpu(skill_config, skill_config_path, resources):
        cpu = "cpu"
        if cpu not in skill_config[resources].keys():
            raise SkillYamlMissingKeyError(resources + ": " + cpu, skill_config_path)
        min = "min"
        cpu_min_entry = resources + ": " + cpu + ": " + min
        if min not in skill_config[resources][cpu]:
            raise SkillYamlMissingKeyError(cpu_min_entry, skill_config_path)
        if not str(skill_config[resources][cpu][min]).isdigit() or int(skill_config[resources][cpu][min]) < 100:
            raise SkillYamlInvalidValueError(cpu_min_entry, skill_config_path)

    @staticmethod
    def validate_memory(skill_config, skill_config_path, resources):
        memory = "memory"
        if memory not in skill_config[resources].keys():
            raise SkillYamlMissingKeyError(resources + ": " + memory, skill_config_path)
        min = "min"
        memory_min_entry = resources + ": " + memory + ": " + min
        if min not in skill_config[resources][memory]:
            raise SkillYamlMissingKeyError(memory_min_entry, skill_config_path)
        if not str(skill_config[resources][memory][min]).isdigit() or int(skill_config[resources][memory][min]) < 128:
            raise SkillYamlInvalidValueError(memory_min_entry, skill_config_path)

    @staticmethod
    def validate_permissions(skill_config, skill_config_path):
        permissions = 'permissions'
        if permissions not in skill_config.keys():
            raise SkillYamlMissingKeyError(permissions, skill_config_path)
        if skill_config[permissions] is None or len(skill_config[permissions]) < 1:
            raise SkillYamlInvalidValueError(permissions, skill_config_path)
        for permission in skill_config[permissions]:
            if not permission:
                raise SkillYamlInvalidValueError(permissions, skill_config_path)

    @staticmethod
    def get_skill_config_path(skill_config_path):
        if skill_config_path is None:
            current_dir = pathlib.Path().absolute()
            skill_config_path = os.path.join(current_dir.parent.parent, 'skill.yml')
        return skill_config_path

    @staticmethod
    def validate_skill_handler(skill_config, skill_config_path):
        handler = SkillTest.validate_handler(skill_config, skill_config_path)
        SkillTest.validate_file(handler, skill_config, skill_config_path)
        SkillTest.validate_function(handler, skill_config, skill_config_path)

    @staticmethod
    def validate_handler(skill_config, skill_config_path):
        handler = 'handler'
        if handler not in skill_config.keys():
            raise SkillYamlMissingKeyError(handler, skill_config_path)
        return handler

    @staticmethod
    def validate_file(handler, skill_config, skill_config_path):
        file = 'file'
        if file not in skill_config[handler].keys():
            raise SkillYamlMissingKeyError(handler + ': ' + file, skill_config_path)
        if not skill_config[handler][file]:
            raise SkillYamlInvalidValueError(handler + ': ' + file, skill_config_path)

    @staticmethod
    def validate_function(handler, skill_config, skill_config_path):
        evaluation_function = 'function'
        if evaluation_function not in skill_config[handler].keys():
            raise SkillYamlMissingKeyError(handler + ': ' + evaluation_function, skill_config_path)
        if not skill_config[handler][evaluation_function]:
            raise SkillYamlInvalidValueError(handler + ': ' + evaluation_function, skill_config_path)

    @staticmethod
    def validate_image(skill_config, skill_config_path):
        image = 'image'
        if image not in skill_config.keys():
            raise SkillYamlMissingKeyError(image, skill_config_path)
        valid_image_pattern = r".+skill-runtime-python-[2,3]\.\d:\d\.\d\.\d"
        if skill_config[image] is None or not re.search(valid_image_pattern, skill_config[image]):
            raise SkillYamlInvalidValueError(image, skill_config_path)

    @staticmethod
    def validate_additional_properties(skill_config, skill_config_path):
        SkillTest.validate_labels(skill_config, skill_config_path)
        SkillTest.validate_authors(skill_config, skill_config_path)

    @staticmethod
    def validate_labels(skill_config, skill_config_path):
        labels = 'labels'
        if labels not in skill_config.keys():
            raise SkillYamlMissingKeyError(labels, skill_config_path)
        if skill_config[labels] is None or len(skill_config[labels]) < 1:
            raise SkillYamlInvalidValueError(labels, skill_config_path)
        for label in skill_config[labels]:
            if not label:
                raise SkillYamlInvalidValueError(labels, skill_config_path)

    @staticmethod
    def validate_authors(skill_config, skill_config_path):
        authors = 'authors'
        if authors not in skill_config.keys():
            raise SkillYamlMissingKeyError(authors, skill_config_path)
        valid_email_pattern = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        if skill_config[authors] is None or len(skill_config[authors]) < 1:
            raise SkillYamlInvalidValueError(authors, skill_config_path)
        for author in skill_config[authors]:
            if not re.search(valid_email_pattern, author):
                raise SkillYamlInvalidValueError(authors, skill_config_path)

    @staticmethod
    def validate_skill_license(skill_config, skill_config_path):
        skill_license = SkillTest.validate_license(skill_config, skill_config_path)
        SkillTest.validate_license_name(skill_license, skill_config, skill_config_path)
        SkillTest.validate_license_url(skill_license, skill_config, skill_config_path)
        SkillTest.validate_license_visibility(skill_config, skill_config_path)

    @staticmethod
    def validate_license_visibility(skill_config, skill_config_path):
        visibility = 'visibility'
        if visibility not in skill_config.keys():
            raise SkillYamlMissingKeyError(visibility, skill_config_path)
        if not skill_config[visibility]:
            raise SkillYamlInvalidValueError(visibility, skill_config_path)

    @staticmethod
    def validate_license(skill_config, skill_config_path):
        skill_license = 'license'
        if skill_license not in skill_config.keys():
            raise SkillYamlMissingKeyError(skill_license, skill_config_path)
        return skill_license

    @staticmethod
    def validate_license_url(skill_license, skill_config, skill_config_path):
        url = 'url'
        if url not in skill_config[skill_license].keys():
            raise SkillYamlMissingKeyError(skill_license + ': ' + url, skill_config_path)
        if not skill_config[skill_license][url] or not validators.url(skill_config[skill_license][url]):
            raise SkillYamlInvalidValueError(skill_license + ': ' + url, skill_config_path)

    @staticmethod
    def validate_license_name(skill_license, skill_config, skill_config_path):
        name = 'name'
        if name not in skill_config[skill_license].keys():
            raise SkillYamlMissingKeyError(skill_license + ': ' + name, skill_config_path)
        if not skill_config[skill_license][name]:
            raise SkillYamlInvalidValueError(skill_license + ': ' + name, skill_config_path)

    @staticmethod
    def validate_skill_identifier(skill_config, skill_config_path):
        SkillTest.validate_owner(skill_config, skill_config_path)
        SkillTest.validate_name(skill_config, skill_config_path)

    @staticmethod
    def validate_version_control(skill_config, skill_config_path):
        scm = 'scm'
        if scm not in skill_config.keys():
            raise SkillYamlMissingKeyError(scm, skill_config_path)

        if not skill_config[scm] or not validators.url(skill_config[scm]):
            raise SkillYamlInvalidValueError(scm, skill_config_path)

    @staticmethod
    def validate_name(skill_config, skill_config_path):
        name = 'name'
        if name not in skill_config.keys():
            raise SkillYamlMissingKeyError(name, skill_config_path)
        if not skill_config[name]:
            raise SkillYamlInvalidValueError(name, skill_config_path)

    @staticmethod
    def validate_owner(skill_config, skill_config_path):
        owner = 'owner'
        if owner not in skill_config.keys():
            raise SkillYamlMissingKeyError(owner, skill_config_path)
        if not skill_config[owner]:
            raise SkillYamlInvalidValueError(owner, skill_config_path)

    @staticmethod
    def make_provision_params_available_in_env(provision_parameter):
        for key in provision_parameter.keys():
            os.environ[key] = provision_parameter[key]
