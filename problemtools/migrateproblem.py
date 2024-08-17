#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import io
import os
import shutil
import sys
import tempfile
import yaml
import yaml.parser

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
        tempdir = None
    else:
        parent, _ = os.path.split(options.outputdir)
        tempdir = tempfile.TemporaryDirectory(dir=parent, delete=False)
        print(tempdir.name)
        shutil.copytree(options.inputdir, tempdir.name, dirs_exist_ok=True)

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

    print(problem_yaml_object)
    key_grader_flags = problem_yaml_object.pop('grader_flags', None)
    match key_grader_flags:
        case None:
            pass
        case 'min' | 'sum':
            problem_yaml_object['aggregation'] = key_grader_flags
        case 'accept_if_any_accepted' | 'always_accept' | 'first_error' | 'ignore_sample' | 'max' | 'worst_error':
            sys.exit(f'unimplemented grader_flags value "{key_grader_flags}"')
        case 'avg':
            sys.exit(f'unsupported grader_flags value "{key_grader_flags}" - this package cannot be migrated')
        case _:
            sys.exit(f'unknown grader_flags value "{key_grader_flags}"')

    print(type(problem_yaml_object))
    print(problem_yaml_object)
