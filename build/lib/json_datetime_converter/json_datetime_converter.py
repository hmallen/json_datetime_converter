import datetime
import json
import logging
import os
import sys

import dateutil.parser

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class JSONDatetimeConverter:
    def __init__(self, conversion_list):
        self.conversion_list = conversion_list


    # Convert to and from types encodable by json module
    def convert_datetime(dt):
        dt_modified = -1

        try:
            if isinstance(dt, datetime.datetime):
                logger.debug('[convert_datetime] datetime.datetime')

                dt_modified = dt.isoformat()

            elif isinstance(dt, str):
                logger.debug('[convert_datetime] str')

                dt_modified = dateutil.parser.parse(dt)

            elif isinstance(dt, datetime.timedelta):
                logger.debug('[convert_datetime] datetime.timedelta')

                dt_modified = dt.total_seconds()

            elif isinstance(dt, float):
                logger.debug('[convert_datetime] float')

                dt_modified = datetime.timedelta(seconds=dt)

            else:
                logger.error('Incorrect type passed to convert_datetime().')

        except Exception as e:
            logger.exception('Exception while converting date/time.')
            logger.exception(e)

        finally:
            return dt_modified


    def read_json(self, json_file):
        json_converted_return = {'data': None, 'status': None}

        #conversion_list = ['heartbeat_last', 'heartbeat_timeout'
                           #'flatline_last', 'flatline_timeout']

        json_data_converted = {}

        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                json_data_raw = json.loads(file.read())

            logger.debug('json_data_raw: ' + str(json_data_raw))

            for data in json_data_raw:
                if data in self.conversion_list:
                    if data == 'heartbeat_last' or data == 'flatline_last':
                        json_data_converted[data] = dateutil.parser.parse(json_data_raw[data])

                    elif data == 'heartbeat_timeout' or data == 'alert_reset_interval':
                        json_data_converted[data] = datetime.timedelta(seconds=json_data_raw[data])

                    else:
                        logger.error('Unknown json data key: ' + data)

                else:
                    json_data_converted[data] = json_data_raw[data]

            json_converted_return['data'] = json_data_converted

            json_converted_return['status'] = True

        except Exception as e:
            logger.exception('Exception in JSONDatetimeConverter.read_json()')
            logger.exception(e)

            json_converted_return['status'] = False

        finally:
            return json_converted_return


    def write_json(self, json_data, json_file):
        json_converted_return = {'data': None, 'status': None}

        #conversion_list = ['heartbeat_last', 'heartbeat_timeout', 'heartbeat_delta',
                           #'flatline_last', 'flatline_timeout', 'flatline_delta']

        json_data_converted = {}

        try:
            for data in json_data:
                if data in self.conversion_list:
                    json_data_converted[data] = JSONDatetimeConverter.convert_datetime(json_data[data])

                else:
                    json_data_converted[data] = json_data[data]

                logger.debug('json_data_converted[data]: ' + str(json_data_converted[data]))

            json_file_new = json_file.rstrip('.json') + '_modified.json'

            with open(json_file_new, 'w', encoding='utf-8') as file:
                json.dump(json_data_converted, file, indent=4, sort_keys=True, ensure_ascii=False)

            json_converted_return['status'] = True

        except Exception as e:
            logger.exception('Exception in JSONDatetimeConverter.write_json()')
            logger.exception(e)

            json_converted_return['status'] = False

        finally:
            return json_converted_return


if __name__ == '__main__':
    conversion_list = ['heartbeat_last', 'heartbeat_timeout',
                       'flatline_last', 'alert_reset_interval']

    json_dt_converter = JSONDatetimeConverter(conversion_list=conversion_list)

    test_file = 'test.json'

    json_data = json_dt_converter.read_json(test_file)

    print('json_data[\'data\']: ', json_data['data'])
    print('json_data[\'status\']: ', json_data['status'])

    json_data['data']['heartbeat_last'] = datetime.datetime.now()

    json_data = json_dt_converter.write_json(json_data=json_data['data'], json_file=test_file)

    print('json_data[\'data\']: ', json_data['data'])
    print('json_data[\'status\']: ', json_data['status'])
