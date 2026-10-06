import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('environment_tool',ROOT/'tools/record_environment.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class EnvironmentRecordTests(unittest.TestCase):
    def dist(self,name,version='1.0'):
        return SimpleNamespace(metadata={'Name':name},version=version)
    def test_package_names_are_normalized_and_sorted(self):
        self.assertEqual(module.package_rows([self.dist('Z_package'),self.dist('A.Name','2.0rc1')]),
                         [dict(name='a-name',version='2.0rc1'),dict(name='z-package',version='1.0')])
    def test_alias_duplicates_are_rejected(self):
        with self.assertRaises(ValueError):module.package_rows([self.dist('some_name'),self.dist('Some-Name')])
    def test_requirement_injection_is_rejected(self):
        for dist in [self.dist('pkg\nother'),self.dist('pkg','1.0\nother==2'),self.dist('pkg','https://example.com/pkg')]:
            with self.assertRaises(ValueError):module.package_rows([dist])
    def test_version_or_platform_drift_is_reported(self):
        original=dict(python_version='3.9.6',python_implementation='CPython',system='Darwin',machine='arm64',packages=[])
        self.assertEqual(module.differences(original,dict(original)),{})
        for key,value in [('python_version','3.10.0'),('machine','x86_64'),('packages',[dict(name='pkg',version='1')])]:
            changed=dict(original);changed[key]=value
            self.assertEqual(set(module.differences(original,changed)),{key})
