#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from modules.utests.test_InterpolationModel import TestInterpolationModel
from service.utests.test_InterpolationModel_rest_api import TestInterpolationModelRestAPI
from modules.utests.test_GenerateModel import TestGenerateModel
from service.utests.test_GenerateModel_rest_api import TestGenerateModelRestAPI


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestInterpolationModel('test_interpolation'))
    suite.addTest(TestInterpolationModelRestAPI('test_service_httpok_json_valid'))
    suite.addTest(TestInterpolationModelRestAPI('test_service_empty_request'))
    suite.addTest(TestInterpolationModelRestAPI('test_service_corrupted_request'))

    suite.addTest(TestGenerateModel('test_generate'))
    suite.addTest(TestGenerateModelRestAPI('test_service_httpok_json_valid'))
    suite.addTest(TestGenerateModelRestAPI('test_service_empty_request'))
    suite.addTest(TestGenerateModelRestAPI('test_service_corrupted_request'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite())
