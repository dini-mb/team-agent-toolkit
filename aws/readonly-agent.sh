#!/bin/bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  printf 'Usage: %s <source-profile> <target-role-arn>\n' "$0" >&2
  exit 2
fi

source_profile="$1"
target_role_arn="$2"

aws sts assume-role \
  --profile "$source_profile" \
  --role-arn "$target_role_arn" \
  --role-session-name "ReadOnlyAgentSession" \
  --policy-arns "arn=arn:aws:iam::aws:policy/ReadOnlyAccess" \
  --query "Credentials.[AccessKeyId, SecretAccessKey, SessionToken, Expiration]" \
  --output json \
  --no-cli-pager |
  jq '{
    Version: 1,
    AccessKeyId: .[0],
    SecretAccessKey: .[1],
    SessionToken: .[2],
    Expiration: .[3]
  }'