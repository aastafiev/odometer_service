# -*- coding: utf-8 -*-

import unittest
import asyncio

import os
import json
from dateutil.parser import parse

import settings as st
from modules.generate import generate_gen
from modules.common.common_func import ClientLastRow, to_java_date_str


class TestGenerateModel(unittest.TestCase):
    def setUp(self):
        test_source_path = os.path.join(st.PROJECT_DIR, 'utests', 'data', 'GenerateModel_source.json')
        test_target_path = os.path.join(st.PROJECT_DIR, 'utests', 'data', 'GenerateModel_target.json')
        with open(test_source_path, 'r') as jin1, open(test_target_path, 'r') as jin2:
            source = json.load(jin1)
            self.expected_values = sorted(json.load(jin2), key=lambda x: parse(x['date_service']))

        self.test_source = ClientLastRow(
            client_name=source['client_name'],
            vin=source['vin'],
            model=source['model'],
            date_service=parse(source['date_service']),
            odometer=source['odometer'],
            day_mean_km=source['day_mean_km'],
            exp_work_type=source['exp_work_type']
        )

    def check_values(self, source, target):
        self.assertIsInstance(source, dict,
                              'The data model returns wrong output type. Expected <list> of <dicts>.')
        self.assertEqual(source['client_name'], target['client_name'],
                         'Returned data corrupted in client_name value.')
        self.assertEqual(source['vin'], target['vin'], 'Returned data corrupted in vin value.')
        self.assertEqual(source['model'], target['model'], 'Returned data corrupted in model value.')
        self.assertEqual(source['date_service'], to_java_date_str(parse(target['date_service'])),
                         'Returned data corrupted in date_service value.')
        self.assertTrue(target['odometer'] - 2 <= source['odometer'] <= target['odometer'] + 2,
                        'Returned data corrupted in service value.')
        self.assertEqual(source['exp_work_type'], target['exp_work_type'],
                         'Returned data corrupted in exp_work_type value.')

    def test_generate(self):
        async def _test_generate():
            res_rows = [res async for res in generate_gen(self.test_source, parse('2017-11-01T00:00:00+0300'))]
            for res_row, control_row in zip(res_rows, self.expected_values):
                self.check_values(res_row, control_row)

        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        try:
            coro = asyncio.coroutine(_test_generate)
            event_loop.run_until_complete(coro())
        finally:
            event_loop.run_until_complete(event_loop.shutdown_asyncgens())
            event_loop.close()

