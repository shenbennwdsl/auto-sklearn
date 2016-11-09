import unittest
import warnings
import re

from unittest.mock import patch, Mock

import pkg_resources

from autosklearn.util.dependencies import verify_packages, _verify_package


@patch('pkg_resources.get_distribution')
class VerifyPackagesTests(unittest.TestCase):

    def test_existing_package(self, getDistributionMock):
        requirement = 'package'

        with warnings.catch_warnings(record=True) as w:
            verify_packages(requirement)
            self.assertEqual(0, len(w))

        getDistributionMock.assert_called_once_with('package')

    def test_missing_package(self, getDistributionMock):
        requirement = 'package'

        getDistributionMock.side_effect = pkg_resources.DistributionNotFound()

        self.assertWarnsRegex(UserWarning, "mandatory package 'package' not found", verify_packages, requirement)

    def test_correct_package_versions(self, getDistributionMock):
        requirement = 'package==0.1.2\n' \
                      'package>0.1\n' \
                      'package>=0.1'

        moduleMock = Mock()
        moduleMock.version = '0.1.2'
        getDistributionMock.return_value = moduleMock

        with warnings.catch_warnings(record=True) as w:
            verify_packages(requirement)
            self.assertEqual(0, len(w))

        getDistributionMock.assert_called_with('package')
        self.assertEqual(3, len(getDistributionMock.call_args_list))

    def test_wrong_package_version(self, getDistributionMock):
        requirement = 'package>0.1.2'

        moduleMock = Mock()
        moduleMock.version = '0.1.2'
        getDistributionMock.return_value = moduleMock

        self.assertWarnsRegex(UserWarning, re.escape("'package' version mismatch (>0.1.2)"), verify_packages, requirement)

    def test_outdated_requirement(self, getDistributionMock):
        requirement = 'package>=0.1'

        moduleMock = Mock()
        moduleMock.version = '0.0.9'
        getDistributionMock.return_value = moduleMock

        self.assertWarnsRegex(UserWarning, re.escape("'package' version mismatch (>=0.1)"), verify_packages, requirement)

    def test_too_fresh_requirement(self, getDistributionMock):
        requirement = 'package==0.1.2'

        moduleMock = Mock()
        moduleMock.version = '0.1.3'
        getDistributionMock.return_value = moduleMock

        self.assertWarnsRegex(UserWarning, re.escape("'package' version mismatch (==0.1.2)"), verify_packages, requirement)