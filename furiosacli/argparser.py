import argparse

def create_argparser():
    parser = argparse.ArgumentParser(description='Furiosa AI Web Service CLI')
    parser.add_argument("-q", "--quiet", action="store_true",
                        help='Quiet mode, CLI will not print out any message', )
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Dnable debug mode")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")

    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser("version", help = 'Print out the version')

    compile_cmd = subparsers.add_parser("compile", help = 'Compile your model and generate a binary for Furiosa NPU')
    compile_cmd.add_argument('source', type=str,
                        help='Path to Model file (tflite, onnx, other renegade internal formats are supported)')
    compile_cmd.add_argument('-o', type=str,
                             help='Path to Output file')
    compile_cmd.add_argument('--target-ir', type=str, default='enf',
                             help='Target IR (available IRs: dfg, cdfg, gir, lir, enf)')
    compile_cmd.add_argument('--config', type=str,
                             help='Path to Compiler Config file (yaml)')
    compile_cmd.add_argument('--target-npu-spec', type=str,
                             help='Path to Target NPU Specification (yaml)')

    perfeye_cmd = subparsers.add_parser("perfeye", help='Generate a visialized view of the static performance estimation')
    add_perf_opts(perfeye_cmd, 'html')
    return parser


def add_perf_opts(parser, content_type):
    parser.add_argument('source', type=str,
                        help='Path to Model file (tflite, onnx, other renegade internal formats are supported)')
    parser.add_argument('-o', type=str, default='output.{}'.format(content_type),
                        help='Path to Output file')
    parser.add_argument('--config', type=str,
                        help='Path to Compiler Config file (yaml)')
    parser.add_argument('--target-npu-spec', type=str,
                        help='Path to Target NPU Specification (yaml)')