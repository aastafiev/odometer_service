# -*- coding: utf-8 -*-

from datetime import datetime
from typing import AsyncIterable

from dateutil.relativedelta import relativedelta
from dateutil.tz import tzlocal

import modules.common.common_func as local_funcs


async def generate_gen(client_last_row: local_funcs.ClientLastRow, date_from: datetime = None) -> AsyncIterable[dict]:
    assert client_last_row, 'client data empty'

    local_tz = tzlocal()
    today = datetime.now(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
    if not date_from:
        if (today - client_last_row.date_service).days > 31:
            date_from = today
        else:
            return

    date_to = date_from + relativedelta(day=31) if 1 <= date_from.day <= 10 else date_from + relativedelta(months=1,
                                                                                                           day=31)

    # check year expire
    difference_in_years = (date_to - client_last_row.date_service).days / 365
    if difference_in_years >= 1:
        yield {'client_name': client_last_row.client_name, 'vin': client_last_row.vin,
               'model': client_last_row.model, 'date_service': local_funcs.to_java_date_str(date_to),
               'odometer': -1, 'exp_work_type': 'year expired: {:.3f}'.format(difference_in_years)}

    if not date_to.tzinfo:
        date_to = date_to.replace(tzinfo=local_tz)

    generated_days = local_funcs.date_range(client_last_row.date_service, date_to)
    next(generated_days)
    for _n, day in enumerate(generated_days, 1):
        new_odometer = client_last_row.odometer + _n * client_last_row.day_mean_km
        new_exp_work_type = local_funcs.calc_exp_work_type(new_odometer, client_last_row.service_period)
        if day >= date_from and new_exp_work_type and new_exp_work_type != client_last_row.exp_work_type:
            yield {'client_name': client_last_row.client_name, 'vin': client_last_row.vin,
                   'model': client_last_row.model, 'date_service': local_funcs.to_java_date_str(day),
                   'odometer': new_odometer, 'exp_work_type': new_exp_work_type}
