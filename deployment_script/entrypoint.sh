#!/usr/bin/env bash
set -e;
if [ -z "$SSH_PRIVATE_KEY" ]; then
    echo "SSH_PRIVATE_KEY must be defined"
fi
eval $(ssh-agent -s)
ssh-add <(echo "$SSH_PRIVATE_KEY")
if [ -n "$UPDATE_TASK" ]; then
    bash update.sh -r $REPO_URL -b $BRANCH -h $HOST -l $USER
else    
    bash deploy.sh -r $REPO_URL -b $BRANCH -p $POSTGRES_USER -P $POSTGRES_PASSWORD -h $HOST -l $USER
fi
