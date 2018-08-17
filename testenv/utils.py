# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import json
import re
import sys
import time
from datetime import datetime

import lxml.etree as etree
import yaml
from lxml import objectify

from testenv.settings import SPID_ERRORS

TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
TIME_FORMAT_WITH_FRAGMENT = re.compile(
    '^(\d{4,4}-\d{2,2}-\d{2,2}T\d{2,2}:\d{2,2}:\d{2,2})(\.\d*)?Z?$')


def get_config(f_name, f_type='yaml'):
    """
    Read server configuration from a json file
    """
    with open(f_name, 'r') as fp:
        if f_type == 'yaml':
            return yaml.load(fp)
        elif f_type == 'json':
            return json.loads(fp.read())


def get_spid_error(code):
    error_type = SPID_ERRORS.get(code)
    return error_type, 'ErrorCode nr{}'.format(code)


def check_utc_date(date):
    try:
        str_to_struct_time(date)
    except Exception:
        return False
    return True


def check_url(url):
    regex = re.compile(r'^https?://(\w+\.)*\w+\.\w+(:\d+)*$')
    is_matching = True if re.match(regex, url) else False
    return is_matching


check_utc_date.error_msg = 'la data non è in formato UTC'
check_url.error_msg = 'la url non è in formato corretto'


def str_to_datetime(val):
    try:
        return datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        try:
            return datetime.strptime(val, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            pass


def str_to_struct_time(timestr, format=TIME_FORMAT):
    """
    :param timestr:
    :param format:
    :return: UTC time
    """
    if not timestr:
        return 0
    try:
        then = time.strptime(timestr, format)
    except ValueError:  # assume it's a format problem
        try:
            elem = TIME_FORMAT_WITH_FRAGMENT.match(timestr)
        except Exception as exc:
            print('Exception: %s on %s' % (exc, timestr), file=sys.stderr)
            raise
        then = time.strptime(elem.groups()[0] + 'Z', TIME_FORMAT)

    return time.gmtime(calendar.timegm(then))


def prettify_xml(msg):
    msg = etree.tostring(
        msg,
        pretty_print=True,
    )
    return msg.decode('utf-8')


def saml_to_dict(xmlstr):
    root = objectify.fromstring(xmlstr)
    def _obj(elem):
        return {
            'attrs': dict(elem.attrib),
            'children': {
                k.tag: _obj(k)
            for k in elem.iterchildren()
            },
            'text': elem.text
        }
    return {
        root.tag: _obj(root)
    }
