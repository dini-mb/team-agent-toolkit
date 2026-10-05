#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
home_dir=${HOME:?HOME must be set}
timestamp=$(date +%Y%m%d%H%M%S)

mkdir -p "$home_dir/.copilot" "$home_dir/.aws"

install_file() {
  source_file=$1
  target_file=$2
  mode=$3
  target_dir=$(dirname "$target_file")
  mkdir -p "$target_dir"

  if [ -L "$target_file" ]; then
    printf 'Refusing to replace symlink: %s\n' "$target_file" >&2
    return 1
  fi

  if [ -f "$target_file" ] && cmp -s "$source_file" "$target_file"; then
    printf 'Unchanged: %s\n' "$target_file"
    return 0
  fi

  if [ -e "$target_file" ]; then
    backup_file="$target_file.backup.$timestamp"
    if [ -e "$backup_file" ]; then
      printf 'Backup already exists, refusing to overwrite: %s\n' "$backup_file" >&2
      return 1
    fi
    cp -p "$target_file" "$backup_file"
    printf 'Backed up: %s\n' "$backup_file"
  fi

  cp "$source_file" "$target_file"
  chmod "$mode" "$target_file"
  printf 'Installed: %s\n' "$target_file"
}

install_file "$repo_dir/instructions/copilot-instructions.md" "$home_dir/.copilot/copilot-instructions.md" 644
install_file "$repo_dir/skills/aws-cli/SKILL.md" "$home_dir/.copilot/skills/aws-cli/SKILL.md" 644
install_file "$repo_dir/skills/create-pr/SKILL.md" "$home_dir/.copilot/skills/create-pr/SKILL.md" 644
install_file "$repo_dir/skills/update-jira-task/SKILL.md" "$home_dir/.copilot/skills/update-jira-task/SKILL.md" 644
install_file "$repo_dir/skills/work-on-jira-task/SKILL.md" "$home_dir/.copilot/skills/work-on-jira-task/SKILL.md" 644
install_file "$repo_dir/hooks/aws-profile-safety.json" "$home_dir/.copilot/hooks/aws-profile-safety.json" 644
install_file "$repo_dir/hooks/deny-aws-non-agent-profile.py" "$home_dir/.copilot/hooks/deny-aws-non-agent-profile.py" 644
install_file "$repo_dir/hooks/terraform-safety.json" "$home_dir/.copilot/hooks/terraform-safety.json" 644
install_file "$repo_dir/hooks/deny-terraform-deploy.py" "$home_dir/.copilot/hooks/deny-terraform-deploy.py" 644
install_file "$repo_dir/aws/readonly-agent.sh" "$home_dir/.aws/readonly-agent.sh" 755

printf '\nReview aws/config.example and manually add the appropriate sections to %s/.aws/config.\n' "$home_dir"