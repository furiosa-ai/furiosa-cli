import os
import subprocess
import unittest

from furiosacli import argparser


class ParserTest(unittest.TestCase):
    source = 'test_data/MNISTnet_uint8_quant_without_softmax.tflite';
    #target_npu_spec = 'test_data/128dpes.yml'
    compiler_config = 'test_data/compiler_config.yml'
    invalid_compiler_config = 'test_data/invalid_compiler_config.yml'

    def setUp(self):
        self.parser = argparser.create_argparser()

    def test_no_command(self):
        result = subprocess.run(['furiosa'], capture_output=True)
        self.assertIn('ERROR: Need command', str(result.stderr))

    def test_compile(self):
        result = subprocess.run(['furiosa',
                                 '-d',
                                 '-v',
                                 'compile', self.source,
                                ], capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('output.enf has been generated', str(result.stdout))

    def test_compile_only_target_npu_spec(self):
        result = subprocess.run(['furiosa',
                                 '-d',
                                 '-v',
                                 'compile', self.source,
                                 #'--target-npu-spec', self.target_npu_spec
                                ], capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('output.enf has been generated', str(result.stdout))

    def test_compile_with_compiler_config(self):
        result = subprocess.run(['furiosa',
                                 '-d',
                                 '-v',
                                 'compile',
                                 self.source,
                                 #'--target-npu-spec', self.target_npu_spec,
                                 '--config', self.compiler_config
                                 ],
                                capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('output.enf has been generated', str(result.stdout))

    def test_compile_with_target_ir(self):
        result = subprocess.run(['furiosa',
                                 '-d',
                                 '-v',
                                 'compile',
                                 self.source,
                                 #'--target-npu-spec', self.target_npu_spec,
                                 '--config', self.compiler_config,
                                 '--target-ir', 'lir'
                                 ],
                                capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('output.lir has been generated', str(result.stdout))

    def test_compile_with_specific_output(self):
        result = subprocess.run(['furiosa',
                                 '-d',
                                 '-v',
                                 'compile',
                                 self.source,
                                 #'--target-npu-spec', self.target_npu_spec,
                                 '--config', self.compiler_config,
                                 '--target-ir', 'lir',
                                 '-o', '/tmp/test.lir',
                                 ],
                                capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('/tmp/test.lir has been generated', str(result.stdout))

    def test_compile_with_reports(self):
        import uuid

        compiler_report_file = '/tmp/{}.txt'.format(uuid.uuid4())
        mem_alloc_report_file = '/tmp/{}.html'.format(uuid.uuid4())

        result = subprocess.run(['furiosa',
                                 '-d',
                                 '-v',
                                 'compile',
                                 self.source,
                                 '--config', self.compiler_config,
                                 '--compiler-report', compiler_report_file,
                                 '--mem-alloc-report', mem_alloc_report_file,
                                 '-o', '/tmp/test.lir'
                                 ],
                                capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('/tmp/test.lir has been generated', str(result.stdout))
        self.assertTrue(os.path.isfile(compiler_report_file))
        self.assertTrue(os.path.isfile(mem_alloc_report_file))

        os.remove(compiler_report_file)
        os.remove(mem_alloc_report_file)


    def test_compile_with_invalid_config(self):
        result = subprocess.run(['furiosa',
                                 '-d',
                                 'compile',
                                 self.source,
                                 #'--target-npu-spec', self.target_npu_spec,
                                 '--config', self.invalid_compiler_config,
                                 ],
                                capture_output=True)
        self.assertEqual(4, result.returncode)
        self.assertIn('ERROR: fail to compile test_data/MNISTnet_uint8_quant_without_softmax.tflite (http_status: 501',
                      str(result.stderr))

    def test_perfeye(self):
        result = subprocess.run(['furiosa',
                                 '-v',
                                 'perfeye',
                                 self.source,
                                 '--config', self.compiler_config,
                                 '-o', '/tmp/test.html',
                                 ],
                                capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('/tmp/test.html has been generated', str(result.stdout))

    def test_perfeye_with_compiler_config(self):
        result = subprocess.run(['furiosa',
                                 '-v',
                                 'perfeye',
                                 self.source,
                                 '--config', self.compiler_config,
                                 '-o', '/tmp/test.html',
                                 ],
                                capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('/tmp/test.html has been generated', str(result.stdout))

    def test_perfeye_with_target_npu_spec(self):
        result = subprocess.run(['furiosa',
                                 '-v',
                                 'perfeye',
                                 self.source,
                                 #'--target-npu-spec', self.target_npu_spec,
                                 '--config', self.compiler_config,
                                 '-o', '/tmp/test.html',
                                 ],
                                capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('/tmp/test.html has been generated', str(result.stdout))