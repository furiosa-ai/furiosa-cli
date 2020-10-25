from typing import List, Dict, Tuple

import json
import uuid

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import yaml
import logging

from furiosacli import consts, __version__
from furiosacli.exceptions import CliError, ApiError


class ApiKeyAuth(requests.auth.AuthBase):
    def __init__(self, session):
        self.session = session

    def __call__(self, r):
        r.headers[consts.ACCESS_KEY_ID_HTTP_HEADER] = self.session.access_key_id
        r.headers[consts.SECRET_ACCESS_KEY_HTTP_HEADER] = self.session.secret_key_access
        return r


class Command(object):
    def __init__(self, session, args, args_map):
        self.session = session
        self.args = args
        self.args_map = args_map

    def print_message(self, msg):
        if not self.args.quiet:
            print(msg)

    def run(self) -> int:
        pass


def read_config_file(path: str):
    with open(path, 'r') as yaml_file:
        yaml_obj = yaml.safe_load(yaml_file)
        return json.dumps(yaml_obj)


def pretty_yaml(json) -> str:
    return yaml.dump(json, default_flow_style=False)


def handle_target_npu_spec(args) -> str:
    if args.target_npu_spec is not None:
        return read_config_file(args.target_npu_spec)
    else:
        # raise CliError('--target-npu-spec is required')
        return '{}'


def handle_compiler_config(args) -> str:
    if args.config is not None:
        return read_config_file(args.config)
    else:
        return '{}'


def handle_target_ir(args_map) -> str:
    if args_map['target_ir'] not in consts.SUPPORT_TARGET_IRS:
        raise CliError('target-ir must be one of {}'.format(consts.SUPPORT_TARGET_IRS))
    else:
        return args_map['target_ir']


class Version(Command):
    def __init__(self, session, args, args_map):
        super().__init__(session, args, args_map)

    def run(self) -> int:
        self.print_message("Version: {}".format(__version__))


class Compile(Command):
    def __init__(self, session, args, args_map):
        super().__init__(session, args, args_map)

    def run(self) -> int:
        source_path = self.args_map['source']
        target_npu_spec = handle_target_npu_spec(self.args)
        compiler_config = handle_compiler_config(self.args)
        target_ir = handle_target_ir(self.args_map)

        if 'o' in self.args and self.args_map['o'] is not None:
            output_path = self.args_map['o']
        else:
            output_path = 'output.{}'.format(target_ir)

        multi_parts = MultipartEncoder(
            fields={
                'target_npu_spec': target_npu_spec,
                'compiler_config': compiler_config,
                'target_ir': target_ir,
                'source': (source_path, open(source_path, mode='rb'), 'application/octet-stream')
            }
        )

        request_url = '{}/compiler'.format(self.session.api_endpoint)
        headers = {
            consts.REQUEST_ID_HTTP_HEADER: str(uuid.uuid4()),
            'Content-Type': multi_parts.content_type
        }

        logging.debug("submitting the compilation request to {}".format(request_url))
        logging.debug("source path: {}".format(source_path))
        logging.debug("output path: {}".format(output_path))
        logging.debug("target ir: {}".format(target_ir))
        logging.debug("target npu spec: \n{}\n".format(pretty_yaml(target_npu_spec)))
        logging.debug("compiler config: \n{}\n".format(pretty_yaml(compiler_config)))

        r = requests.post(request_url,
                          data=multi_parts,
                          headers=headers,
                          auth=ApiKeyAuth(self.session))

        if r.status_code == 200:
            with open(output_path, 'wb') as output_file:
                content = r.content
                output_file.write(content)

                ms_elapsed = r.elapsed.microseconds / 1000
                self.print_message('{} has been generated (elapsed: {} ms)'.format(output_path, ms_elapsed))
        else:
            raise ApiError('fail to compile {}'.format(source_path), r)


class Perf(Command):
    def __init__(self, session, args, args_map, api_path='perf', content_type='csv'):
        super().__init__(session, args, args_map)
        self.api_path = api_path
        self.content_type = content_type

    def run(self) -> int:
        source_path = self.args_map['source']
        target_npu_spec = handle_target_npu_spec(self.args)
        compiler_config = handle_compiler_config(self.args)

        if 'o' in self.args and self.args_map['o'] is not None:
            output_path = self.args_map['o']
        else:
            output_path = 'output.{}'.format(self.content_type)

        multi_parts = MultipartEncoder(
            fields={
                'target_npu_spec': target_npu_spec,
                'compiler_config': compiler_config,
                'source': (source_path, open(source_path, mode='rb'), 'application/octet-stream')
            }
        )

        request_url = '{}/{}'.format(self.session.api_endpoint, self.api_path)
        headers = {
            consts.REQUEST_ID_HTTP_HEADER: str(uuid.uuid4()),
            'Content-Type': multi_parts.content_type
        }

        logging.debug("submitting the perf request to {}".format(request_url))
        logging.debug("source path: {}".format(source_path))
        logging.debug("output path: {}".format(output_path))
        logging.debug("target npu spec: \n{}\n".format(pretty_yaml(target_npu_spec)))
        logging.debug("compiler config: \n{}\n".format(pretty_yaml(compiler_config)))

        r = requests.post(request_url,
                          data=multi_parts,
                          headers=headers,
                          auth=ApiKeyAuth(self.session))

        if r.status_code == 200:
            with open(output_path, 'wb') as output_file:
                content = r.content
                output_file.write(content)

                ms_elapsed = r.elapsed.microseconds / 1000
                self.print_message('{} has been generated (elapsed: {} ms)'.format(output_path, ms_elapsed))
        else:
            raise ApiError('fail to estimate the performance {}'.format(source_path), r)


class Perfeye(Perf):
    def __init__(self, session, args, args_map):
        super().__init__(session, args, args_map, api_path='perfeye', content_type='html')


class BuildCalibrationModel(Command):
    def __init__(self, session, args, args_map):
        super().__init__(session, args, args_map)

    @staticmethod
    def build_calibration_model(session,
                                model: bytes,
                                input_tensors: List[str],
                                model_path: str = None) -> bytes:
        model_path = model_path or 'model.onnx'
        multi_parts = MultipartEncoder(
            fields={
                'input_tensors': json.dumps(input_tensors),
                'source': (model_path, model, 'application/octet-stream')
            }
        )

        request_url = '{}/dss/build-calibration-model'.format(session.api_endpoint)
        headers = {
            consts.REQUEST_ID_HTTP_HEADER: str(uuid.uuid4()),
            'Content-Type': multi_parts.content_type
        }

        logging.debug("submitting the build calibration model request to {}".format(request_url))
        logging.debug("source path: {}".format(model_path))
        logging.debug("input tensors: \n{}\n".format(input_tensors))

        r = requests.post(request_url,
                          data=multi_parts,
                          headers=headers,
                          auth=ApiKeyAuth(session))

        if r.status_code == 200:
            return r.content
        else:
            raise ApiError('fail to build calibration model {}'.format(model_path), r)

    def run(self) -> int:
        source_path = self.args_map['source']
        input_tensors = self.args_map['input_tensors']

        if 'o' in self.args and self.args_map['o'] is not None:
            output_path = self.args_map['o']
        else:
            output_path = 'output.onnx'

        with open(source_path, 'rb') as model, \
                open(output_path, 'wb') as output_file:
            model = BuildCalibrationModel.build_calibration_model(self.session,
                                                                  model.read(),
                                                                  input_tensors,
                                                                  model_path=source_path)
            output_file.write(model)


class Quantize(Command):
    def __init__(self, session, args, args_map):
        super().__init__(session, args, args_map)

    @staticmethod
    def quantize(session,
                 model: bytes,
                 input_tensors: List[str],
                 dynamic_ranges: Dict[str, Tuple[float, float]],
                 model_path: str = None) -> bytes:
        model_path = model_path or 'model.onnx'
        multi_parts = MultipartEncoder(
            fields={
                'input_tensors': json.dumps(input_tensors),
                'dynamic_ranges': json.dumps(dynamic_ranges),
                'source': (model_path, model, 'application/octet-stream')
            }
        )

        request_url = '{}/dss/quantize'.format(session.api_endpoint)
        headers = {
            consts.REQUEST_ID_HTTP_HEADER: str(uuid.uuid4()),
            'Content-Type': multi_parts.content_type
        }

        logging.debug("submitting the quantize request to {}".format(request_url))
        logging.debug("source path: {}".format(model_path or 'model.onnx'))
        logging.debug("input tensors: \n{}\n".format(input_tensors))
        logging.debug("dynamic ranges: \n{}\n".format(dynamic_ranges))

        r = requests.post(request_url,
                          data=multi_parts,
                          headers=headers,
                          auth=ApiKeyAuth(session))

        if r.status_code == 200:
            return r.content
        else:
            raise ApiError('fail to quantize th model {}'.format(model_path), r)

    def run(self) -> int:
        source_path = self.args_map['source']
        input_tensors = self.args_map['input_tensors']
        dynamic_ranges = self.args_map['dynamic_ranges']

        if 'o' in self.args and self.args_map['o'] is not None:
            output_path = self.args_map['o']
        else:
            output_path = 'output.onnx'

        with open(source_path, 'rb') as model, \
                open(dynamic_ranges, 'r') as dynamic_ranges, \
                open(output_path, 'wb') as output_file:
            dynamic_ranges = json.load(dynamic_ranges)
            model = Quantize.quantize(self.session,
                                      model.read(),
                                      input_tensors,
                                      dynamic_ranges,
                                      model_path=source_path)
            output_file.write(model)
