#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
import argparse
import io
import os
import shutil
import sys
import tempfile
import yaml
import yaml.parser

def dict_add_unless_none(dict, key, value):
    if value is not None:
        dict[key] = value

class ProblemFormatVersion(Enum):
    LEGACY = 1
    LEGACY_ICPC = 2
    V2023_07 = 3

class ProblemYaml:
    def __init__(self, format_version):
        if format_version is None or format_version == 'legacy':
            self._version_enum = ProblemFormatVersion
            self._format_version = 'legacy'
        else:
            sys.exit(f'unimplemented problem format version: {format_version}')
        self._type = None
        self._name = None
        self._author = None
        self._source = None
        self._source_url = None
        self._license = None
        self._rights_owner = None
        self._limits = None
        self._validation = None
        self._validator_flags = None
        self._scoring = None
        self._keywords = None

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value is not None:
            if value not in ['pass-fail', 'scoring']:
                sys.exit(f'unknown problem type: {value}')
            self._type = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is not None:
            self._name = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        if value is not None:
            self._author = value

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        if value is not None:
            self._source = value

    @property
    def source_url(self):
        return self._source_url

    @source_url.setter
    def source_url(self, value):
        if value is not None:
            self._source_url = value

    @property
    def license(self):
        return self._license

    @license.setter
    def license(self, value):
        if value is not None:
            self._license = value

    @property
    def rights_owner(self):
        return self._rights_owner

    @rights_owner.setter
    def rights_owner(self, value):
        if value is not None:
            self._rights_owner = value

    @property
    def limits(self):
        return self._limits

    @limits.setter
    def limits(self, value):
        if value is not None:
            self._limits = value

    @property
    def validation(self):
        return self._validation

    @validation.setter
    def validation(self, value):
        if value is not None:
            self._validation = value

    @property
    def validator_flags(self):
        return self._validator_flags

    @validator_flags.setter
    def validator_flags(self, value):
        if value is not None:
            self._validator_flags = value

    @property
    def scoring(self):
        return self._scoring

    @scoring.setter
    def scoring(self, value):
        if value is not None:
            self._scoring = value

    def grading(self, value):
        if value is not None:
            print('WARNING: "grading" is deprecated, use "scoring" instead', file=sys.stderr)
            self._scoring = value

    @property
    def keywords(self):
        return self._keywords

    @keywords.setter
    def keywords(self, value):
        if value is not None:
            self._keywords = value

    def generate_dict(self):
        dict = {
            "problem_format_version": self._format_version,
        }
        dict_add_unless_none(dict, 'type', self.type)
        dict_add_unless_none(dict, 'name', self.name)
        dict_add_unless_none(dict, 'author', self.author)
        dict_add_unless_none(dict, 'source', self.source)
        dict_add_unless_none(dict, 'source_url', self.source_url)
        dict_add_unless_none(dict, 'license', self.license)
        dict_add_unless_none(dict, 'rights_owner', self.rights_owner)
        dict_add_unless_none(dict, 'limits', self.limits)
        dict_add_unless_none(dict, 'validation', self.validation)
        dict_add_unless_none(dict, 'validator_flags', self.validator_flags)
        dict_add_unless_none(dict, 'scoring', self.scoring)
        dict_add_unless_none(dict, 'keywords', self.keywords)
        return dict

def arg_inputdir(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f'inputdir: {path} is not a valid path')
    return path

def arg_outputdir(path):
    #if os.path.lexists(path):
    #    raise argparse.ArgumentTypeError(f'outputdir: {path} already exists')
    canonical = os.path.realpath(path)
    parent, _ = os.path.split(canonical)
    try:
        os.makedirs(parent, exist_ok=True)
    except OSError as error:
        raise argparse.ArgumentTypeError(f'outputdir: could not create: {error}')
    return canonical

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate (and optionally perform) problem package migration from legacy to current format.')
    parser.add_argument('inputdir', type=arg_inputdir, help='the path to a problem package in legacy format')
    parser.add_argument('-o', '--outputdir', type=arg_outputdir, help='folder of the output package (to be created)')
    options = parser.parse_args()

    if options.outputdir is None:
        parent = None
    else:
        parent, _ = os.path.split(options.outputdir)

    tempdir = tempfile.mkdtemp(prefix='migrateproblem-', dir=parent)
    print(tempdir)
    shutil.copytree(options.inputdir, tempdir, dirs_exist_ok=True)

    try:
        problem_yaml_path = os.path.join(options.inputdir, 'problem.yaml')
        problem_yaml_stream = io.open(problem_yaml_path, 'r')
    except FileNotFoundError:
        sys.exit(f'problem metadata not found in inputdir ({problem_yaml_path})')

    with problem_yaml_stream:
        try:
            problem_yaml_object = yaml.safe_load(problem_yaml_stream)
        except yaml.parser.ParserError as error:
            sys.exit(f'problem metadata parsing failed: {error}')

    problem_yaml = ProblemYaml(problem_yaml_object.pop('problem_format_version', None))
    problem_yaml.type = problem_yaml_object.pop('type', None)
    problem_yaml.name = problem_yaml_object.pop('name', None)
    problem_yaml.author = problem_yaml_object.pop('author', None)
    problem_yaml.source = problem_yaml_object.pop('source', None)
    problem_yaml.source_url = problem_yaml_object.pop('source_url', None)
    problem_yaml.license = problem_yaml_object.pop('license', None)
    problem_yaml.rights_owner = problem_yaml_object.pop('rights_owner', None)
    problem_yaml.limits = problem_yaml_object.pop('limits', None)
    problem_yaml.validation = problem_yaml_object.pop('validation', None)
    problem_yaml.validator_flags = problem_yaml_object.pop('validator_flags', None)
    problem_yaml.scoring = problem_yaml_object.pop('scoring', None)
    problem_yaml.grading(problem_yaml_object.pop('grading', None))
    problem_yaml.keywords = problem_yaml_object.pop('keywords', None)

    if bool(problem_yaml_object):
        print(f'WARNING: superfluous keys in "problem.yaml": {problem_yaml_object}', file=sys.stderr)

    print(f'{problem_yaml.generate_dict()}')

    print(problem_yaml_object)
    # key_grader_flags = problem_yaml_object.pop('grader_flags', None)
    # match key_grader_flags:
    #     case None:
    #         pass
    #     case 'min' | 'sum':
    #         problem_yaml_object['aggregation'] = key_grader_flags
    #     case 'accept_if_any_accepted' | 'always_accept' | 'first_error' | 'ignore_sample' | 'max' | 'worst_error':
    #         sys.exit(f'unimplemented grader_flags value "{key_grader_flags}"')
    #     case 'avg':
    #         sys.exit(f'unsupported grader_flags value "{key_grader_flags}" - this package cannot be migrated')
    #     case _:
    #         sys.exit(f'unknown grader_flags value "{key_grader_flags}"')

    print(type(problem_yaml_object))
    print(problem_yaml_object)
