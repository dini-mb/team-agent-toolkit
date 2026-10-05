import json
import re
import shlex
import sys
from pathlib import PurePosixPath


SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
WRAPPERS = {"command", "exec", "env", "nohup"}
SEPARATORS = set(";&|()\n")
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")


def inspect_segment(tokens, depth):
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if ASSIGNMENT.match(token) or token in {"!", "then", "do"}:
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
    if executable in {"aws", "aws.exe"}:
        profile_found = False
        for argument_index, argument in enumerate(arguments):
            if argument == "--profile":
                profile = arguments[argument_index + 1] if argument_index + 1 < len(arguments) else ""
            elif argument.startswith("--profile="):
                profile = argument.partition("=")[2]
            else:
                continue
            profile_found = True
            if not profile.endswith("-agent"):
                return profile or "<empty>"
        if not profile_found:
            return "<missing>"

    if executable in SHELLS:
        for argument_index, argument in enumerate(arguments):
            if argument.startswith("-") and not argument.startswith("--") and "c" in argument:
                if argument_index + 1 < len(arguments):
                    return blocked_profile(arguments[argument_index + 1], depth + 1)
                break

    return None


def blocked_profile(command, depth=0):
    if depth > 10:
        raise ValueError("Shell nesting exceeds the safety hook limit")

    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace = " \t\r"
    segment = []
    for token in lexer:
        if token and set(token) <= SEPARATORS:
            profile = inspect_segment(segment, depth)
            if profile is not None:
                return profile
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
            profile = blocked_profile(command)
            if profile is not None:
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            f"AWS profile '{profile}' is blocked by the team hook. "
                            "Every AWS CLI command must explicitly pass --profile "
                            "with a value ending in '-agent'."
                        ),
                    }
                }))
                return 0

        print("{}")
        return 0
    except (ValueError, TypeError) as error:
        print(f"AWS profile safety hook cannot inspect this call: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())