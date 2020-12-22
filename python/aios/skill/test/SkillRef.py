from typing import List

from dataclasses import dataclass
import importlib

from dynabuffers.Dynabuffers import Dynabuffers
from antlr4 import FileStream


@dataclass
class SkillRef:
    context: dict

    handler_module: str
    evaluate_function: str
    handler_path: str

    on_started_function = "on_started"
    on_stopped_function = "on_stopped"

    contract_path: str

    def evaluate(self, payload: dict, incoming_namespaces: List[str] = None, outgoing_namespaces: List[str] = None):
        if not incoming_namespaces:
            incoming_namespaces = ["incoming"]
        if not outgoing_namespaces:
            outgoing_namespaces = ["outgoing"]

        function = self.import_function(self.evaluate_function, self.handler_module)
        self._dynabuffers = Dynabuffers.parse(FileStream(self.contract_path))

        parsed_payload = self._dynabuffers.deserialize(self._dynabuffers.serialize(payload, incoming_namespaces), incoming_namespaces)
        response = function(parsed_payload, self.context)
        parsed_response = self._dynabuffers.deserialize(self._dynabuffers.serialize(response, outgoing_namespaces), outgoing_namespaces)

        return parsed_response

    def import_function(self, function_name, module_name):
        module_path = f"src.{module_name}" if self.handler_path is None else self.handler_path

        try:
            module = importlib.import_module(module_path)
            function = getattr(module, function_name)
        except ImportError:
            raise ImportError("Failed to import function {} from module {}".format(function_name, module_name))

        return function

    def on_started(self):
        function = self.import_function(self.on_started_function, self.handler_module)
        function(self.context)

    def on_stopped(self):
        function = self.import_function(self.on_stopped_function, self.handler_module)
        function(self.context)
