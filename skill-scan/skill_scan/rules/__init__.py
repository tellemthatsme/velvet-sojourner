from skill_scan.rules.shell_injection import ShellInjectionRule
from skill_scan.rules.secrets import SecretsRule
from skill_scan.rules.code_exec import CodeExecRule
from skill_scan.rules.obfuscation import ObfuscationRule
from skill_scan.rules.prompt_injection import PromptInjectionRule
from skill_scan.rules.network import NetworkRule
from skill_scan.rules.file_access import FileAccessRule
from skill_scan.rules.exfiltration import ExfiltrationRule

__all__ = [
    "ShellInjectionRule",
    "SecretsRule",
    "CodeExecRule",
    "ObfuscationRule",
    "PromptInjectionRule",
    "NetworkRule",
    "FileAccessRule",
    "ExfiltrationRule",
    "builtin_rules",
]

builtin_rules = [
    ShellInjectionRule(),
    SecretsRule(),
    CodeExecRule(),
    ObfuscationRule(),
    PromptInjectionRule(),
    NetworkRule(),
    FileAccessRule(),
    ExfiltrationRule(),
]
