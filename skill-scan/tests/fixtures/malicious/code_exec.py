"""Malicious skill using dynamic code execution."""

import importlib


def execute_user_code(code_str: str) -> None:
    eval(code_str)


def run_module(module_name: str):
    importlib.import_module(module_name)


def dangerous_compile(src: str):
    compile(src, "<string>", "exec")


def run_system_cmd(cmd: str):
    import os
    os.system(cmd)


if __name__ == "__main__":
    exec("print('pwned')")
