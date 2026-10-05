# Team Agent Toolkit

Shared Copilot skills, instructions, hooks, MCP configuration, and read-only AWS tooling.

## Capabilities

- `aws-cli`: choose a task-matched `-agent` profile for read-only AWS work and permission dry-runs.
- `work-on-jira-task`: inspect tickets, prepare branches, and implement approved changes.
- `create-pr`: prepare and publish PRs with the shared template and verified checks.
- `update-jira-task`: post authorised progress and PR updates to the supplied ticket.
- Atlassian MCP: access Jira and Confluence tools through the hosted server, subject to client sign-in and user permissions.
- Hooks: require explicit `-agent` profiles for visible AWS commands and block Terraform `apply` and `destroy`.

## Repository layout

```text
team-agent-toolkit/
|-- README.md
|-- .gitignore
|-- copilot-instructions.md
|-- install.sh
|-- aws/
|   |-- config.example
|   `-- readonly-agent.sh
|-- hooks/
|   |-- aws-profile-safety.json
|   |-- deny-aws-non-agent-profile.py
|   |-- terraform-safety.json
|   `-- deny-terraform-deploy.py
|-- mcp/
|   `-- mcp-config.json
|-- skills/
|   |-- aws-cli/SKILL.md
|   |-- create-pr/SKILL.md
|   |-- update-jira-task/SKILL.md
|   `-- work-on-jira-task/SKILL.md
`-- tests/
	|-- __init__.py
	`-- test_hooks.py
```

## Setup

From the repository directory, run:

```sh
chmod +x install.sh
./install.sh
```

The installer puts skills, instructions, and hooks under `~/.copilot`, and the credential helper under `~/.aws`. It installs the shared MCP config as `~/.copilot/mcp-config.json` only if that file does not already exist. Merge `mcp/mcp-config.json` manually into an existing config to keep its other servers. Changed destination files are backed up before replacement.

In VS Code, select the Local session target and confirm the hooks appear in Chat Customizations. Hooks must be enabled and the workspace trusted. The installed `~/.copilot/copilot-instructions.md` applies to Copilot Agent Host sessions.

## AWS config

The installer does not modify `~/.aws/config`. Review `aws/config.example`, then add matching sections to your existing config. Replace every placeholder with values from your AWS IAM Identity Center and account setup; do not replace the whole config.

```ini
[sso-session team-sso]
sso_start_url = https://<your-identity-center-domain>.awsapps.com/start
sso_region = <identity-center-region>

[profile project-source]
sso_session = team-sso
sso_account_id = <12-digit-account-id>
sso_role_name = <identity-center-role-name>
region = <default-region>

[profile project-dev-agent]
credential_process = /home/<username>/.aws/readonly-agent.sh project-source arn:aws:iam::<12-digit-account-id>:role/<target-role-name>
region = <default-region>
```

Set the credential-process path to the helper's absolute path. The `-agent` profile uses the source SSO profile to assume the target role with the AWS managed `ReadOnlyAccess` session policy. The target role must trust the source identity and grant the required access; the session policy only limits permissions granted by that role.

Install AWS CLI v2 and `jq`. From your own terminal, start device-code sign-in with:

```sh
aws sso login --use-device-code --no-browser
```

To select the configured source profile explicitly, use:

```sh
aws sso login --use-device-code --no-browser --profile project-source
```

Then check the agent profile with `aws sts get-caller-identity --profile project-dev-agent`. Use an agent profile ending in `-agent` for AWS CLI commands issued by Copilot.

## Guardrails and tests

The AWS hook blocks visible AWS CLI commands that omit `--profile` or use a profile without the `-agent` suffix. The Terraform hook blocks visible `terraform apply` and `terraform destroy` commands. Hooks do not cover manual terminal commands or AWS and Terraform calls hidden inside scripts; IAM policies remain the permissions boundary.

Run the simulated hook tests with:

```sh
python3 -m unittest discover -s tests -v
```
