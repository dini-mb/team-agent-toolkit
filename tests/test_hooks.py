import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_hook(script, command):
    event = {"tool_name": "run_in_terminal", "tool_input": {"command": command}}
    return subprocess.run(
        [sys.executable, str(ROOT / "hooks" / script)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        check=False,
    )


class AwsProfileHookTests(unittest.TestCase):
    def test_requires_agent_profile_for_every_aws_command(self):
        cases = {
            "aws s3 ls": True,
            "AWS_PROFILE=example-agent aws s3 ls": True,
            "aws s3 ls --profile example-agent": False,
            "aws --profile=example-agent s3 ls": False,
            "aws s3 ls --profile example-admin": True,
            "aws s3 ls --profile example-agent && aws ec2 describe-instances": True,
            "aws s3 ls --profile example-agent && aws ec2 describe-instances --profile example-agent": False,
            "bash -c \"aws s3 ls\"": True,
            "zsh -lc \"aws s3 ls --profile example-agent\"": False,
            "echo 'aws s3 ls'": False,
            "git status": False,
        }
        for command, denied in cases.items():
            with self.subTest(command=command):
                result = run_hook("deny-aws-non-agent-profile.py", command)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                is_denied = output.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
                self.assertEqual(is_denied, denied)


class TerraformHookTests(unittest.TestCase):
    def test_blocks_apply_and_destroy(self):
        cases = {
            "terraform plan": False,
            "terraform apply": True,
            "terraform -chdir=stacks/dev destroy -auto-approve": True,
            "terraform plan && terraform apply": True,
            "bash -c \"terraform destroy\"": True,
            "echo terraform apply": False,
            "git status": False,
        }
        for command, denied in cases.items():
            with self.subTest(command=command):
                result = run_hook("deny-terraform-deploy.py", command)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                is_denied = output.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
                self.assertEqual(is_denied, denied)


if __name__ == "__main__":
    unittest.main()