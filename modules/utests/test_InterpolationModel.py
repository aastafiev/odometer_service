# -*- coding: utf-8 -*-

import unittest
import asyncio

import os
import json
from collections import OrderedDict
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzlocal
import itertools

import settings as st
from modules.interpolation import interpolate_gen


class TestInterpolationModel(unittest.TestCase):
    def setUp(self):
        test_rows_path = os.path.join(st.PROJECT_DIR, 'utests', 'data', 'InterpolationModel_source.json')
        test_out_path = os.path.join(st.PROJECT_DIR, 'utests', 'data', 'InterpolationModel_target.json')
        with open(test_rows_path, 'r') as jin1, open(test_out_path, 'r') as jin2:
            test_rows = json.load(jin1)
            self.expected_values = sorted(json.load(jin2),
                                          key=lambda x: parse(x['date_service']))

        self.client_data = OrderedDict()
        for row in test_rows:
            key = parse(row['date_service']).date().isoformat()
            self.client_data[key] = {'client_name': row['client_name'],
                                     'vin': row['vin'],
                                     'model': row['model'],
                                     'odometer': row['odometer'] if row['odometer'] else 0,
                                     'service_period': row['service_period'],
                                     'presence': 1}

    def check_values(self, source, target):
        self.assertIsInstance(source, dict,
                              'The data model returns wrong output type. Expected <list> of <dicts>.')
        self.assertEqual(source['client_name'], target['client_name'],
                         'Returned data corrupted in client_name value.')
        self.assertEqual(source['vin'], target['vin'], 'Returned data corrupted in vin value.')
        self.assertEqual(source['model'], target['model'], 'Returned data corrupted in model value.')
        self.assertEqual(parse(source['date_service']),
                         parse(target['date_service']),
                         'Returned data corrupted in date_service value.')
        self.assertEqual(source['presence'], target['presence'], 'Returned data corrupted in presence value.')
        self.assertEqual(source['exp_work_type'], target['exp_work_type'],
                         'Returned data corrupted in exp_work_type value.')
        self.assertTrue(target['odometer'] - 2 <= source['odometer'] <= target['odometer'] + 2,
                        'Returned data corrupted in service value.')
        if source['km']:
            self.assertTrue(target['km'] - 2 <= source['km'] <= target['km'] + 2,
                            'Returned data corrupted in km value')
        else:
            self.assertEqual(target['km'], source['km'], 'Returned data corrupted in km value')

    def test_interpolation(self):
        async def _test_interpolation():
            def check_by_date(v):
                return parse(v['date_service']) < max_interp_data

            res_rows = [res async for res in interpolate_gen(self.client_data,
                                                             months_mean_lag=-3,
                                                             months_data_lag=-24)]
            for res_row, control_row in zip(res_rows, self.expected_values):
                self.check_values(res_row, control_row)

            max_interp_data = parse('2017-05-25T00:00:00+03:00')
            with_max_interp_date = [res async for res in interpolate_gen(self.client_data,
                                                                         months_mean_lag=-3,
                                                                         max_interp_date=max_interp_data)]
            new_expected_values = itertools.filterfalse(check_by_date, self.expected_values)

            for res_row, control_row in zip(with_max_interp_date, new_expected_values):
                self.check_values(res_row, control_row)

        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        try:
            coro = asyncio.coroutine(_test_interpolation)
            event_loop.run_until_complete(coro())
        finally:
            event_loop.run_until_complete(event_loop.shutdown_asyncgens())
            event_loop.close()
