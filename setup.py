"""setup.py"""
import os
import sys
from setuptools import setup, find_packages, Command

with open("README.md") as f:
    README = f.read()

with open("LICENSE") as f:
    LICENSE = f.read()

class ProtoGenerator(Command):
    """ A custom command """
    description = "Generate Proto Services"
    user_options = [
        ("proto=", 'p' ,"proto directory")
    ]

    def setup_grpc_tools(self):
        try:
            from grpc_tools import protoc
            return protoc
        except ImportError:
            self.announce("Please install grpc_tools!!")
            sys.exit(2)

    def initialize_options(self):
        self.proto = "proto"
    
    def finalize_options(self):
        if self.proto is None:
            raise Exception("Parameter --proto is missing")
    
    def run(self):
        full_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.proto)
        self.announce(f"Scanning: {full_dir}", level=2)
        proto_files = os.listdir(full_dir)
        for filename in proto_files:
            flag = self.process_service_file(filename, full_dir)
            if not flag:
                self.announce(f"Failed Processing Module: {filename}", level=4)
        self.announce("Complete!!", level=2)

    def construct_path(self, fragment, path):
        try:
            os.makedirs(path, exist_ok=True)
            fd = f"{path}/__init__.py"
            fd = open(fd, "w")
            fd.write("# Generated by gen command\n")
            fd.write(f"from .{fragment}_pb2_grpc import *\n")
            fd.write(f"from .{fragment}_pb2 import *\n")
            fd.close()

        except OSError as e:
            self.announce(str(e), level=4)
            self.announce(f"Failed creating: {path}", level=4)

    def replace_relative_import(self, full_path, fragment):
        try:
            fd = open(f"{full_path}/{fragment}_pb2_grpc.py")
            content = fd.read().split("\n")
            content[4] = f"import generated.{fragment}.{fragment}_pb2 as {fragment}__pb2"
            code = "\n".join(content)
            open(f"{full_path}/{fragment}_pb2_grpc.py", "w").write(code)
            return True
        except Exception as e:
            self.announce(str(e), level=2)
            return False

    def process_service_file(self, proto_buf_file, dirname):
        """ create a new service directory for protobufs """
        try:
            proto_tools = self.setup_grpc_tools()
            file_fragment = proto_buf_file.split("/")[-1].split(".")[0]
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated", file_fragment)
            self.construct_path(file_fragment, full_path)
            full_pb_path = os.path.join(dirname, proto_buf_file)
            args = (
                'grpc_tools.protoc',
                f'-I{dirname}',
                f'--python_out={full_path}',
                f'--grpc_python_out={full_path}',
                f"{full_pb_path}"
            )
            proto_tools.main(args)
            self.replace_relative_import(full_path, file_fragment)
            return True
        except Exception as e:
            self.announce(f"Failed compiling: {proto_buf_file}", level=5)
            return False


setup(
    name="grpc-python-starter",
    version="1.0.0",
    url="https://github.com/sourcepirate/grpc-python-starter.git",
    license=LICENSE,
    packages=find_packages(exclude=("tests", "docs")),
    test_suite="tests",
    cmdclass={
        'gen': ProtoGenerator
    },
    scripts=["bin/grpc-py-serve"]
)