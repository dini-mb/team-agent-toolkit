import json
import shlex
import sys
from pathlib import PurePosixPath


BLOCKED_OPERATIONS = {"apply", "destroy"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
WRAPPERS = {"command", "exec", "env", "nohup", "sudo"}
SEPARATORS = set(";&|()\n")


def inspect_segment(tokens, depth):
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in {"!", "then", "do"} or ("=" in token and not token.startswith("-")):
            index += 1
        elif PurePosixPath(token).name in WRAPPERS:
            index += 1
            while index < len(tokens) and tokens[index].startswith("-"):
                index += 1
        else:
            break

    if index == len(tokens):
        return None

    executable = PurePosixPath(tokens[index]).name
    arguments = tokens[index + 1:]
    if executable in {"terraform", "terraform.exe"}:
        skip_value = False
        for argument in arguments:
            if skip_value:
                skip_value = False
                continue
            if argument == "-chdir":
                skip_value = True
                continue
            if argument.startswith("-"):
                continue
            if argument in BLOCKED_OPERATIONS:
                return argument
            return None

    if executable in SHELLS:
        for argument_index, argument in enumerate(arguments):
            if argument and set(argument) <= SEPARATORS:
                break
            if argument.startswith("-") and not argument.startswith("--") and "c" in argument:
                if argument_index + 1 < len(arguments):
                    operation = blocked_operation(arguments[argument_index + 1], depth + 1)
                    if operation:
                        return operation
                break

    return None


def blocked_operation(command, depth=0):
    if depth > 10:
        raise ValueError("Shell nesting exceeds the safety hook limit")

    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace = " \t\r"
    segment = []
    for token in lexer:
        if token and set(token) <= SEPARATORS:
            operation = inspect_segment(segment, depth)
            if operation:
                return operation
            segment = []
        else:
            segment.append(token)
    return inspect_segment(segment, depth)


def commands_from(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"command", "commandLine"} and isinstance(item, str):
                yield item
            elif isinstance(item, (dict, list)):
                yield from commands_from(item)
    elif isinstance(value, list):
        for item in value:
            yield from commands_from(item)


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("Hook input must be a JSON object")
        tool_input = event.get("tool_input", {})
        if not isinstance(tool_input, dict):
            raise ValueError("tool_input must be a JSON object")

        for command in commands_from(tool_input):
            operation = blocked_operation(command)
            if operation:
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            f"terraform {operation} is blocked by the team hook. "
                            "Terraform deployment and destruction must run in the pipeline."
                        ),
                    }
                }))
                return 0

        print("{}")
        return 0
    except (ValueError, TypeError) as error:
        print(f"Terraform safety hook cannot inspect this call: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())