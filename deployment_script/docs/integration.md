# Integration

This document will explain how to integrate this repository with Gitlab and the [django-sample](https://gitlab.devartis.com/samples/django-sample) project.
At the end, a cuple of ssh key (public and private) will be created.
The public key will end at the `.ssh/authorized_keys` in the server and as a `Deploy Key` in Gitlab.
The private key will be added as a `Secret Variable` in Gitlab

## index

- TBD

## Prerequisitos

- A Server with a ssh servise at port `22`
- A privileged user (like `root`)

## Example

For example purposes, let's asume we are setting up a `testing` server with the following variables:

```bash
SERVER=138.197.72.21
USER=root
```

## Setup server && Security

Create a ubuntu:16-04 with a `ssh` service.
Steps taken from [digitalocean](https://www.digitalocean.com/community/tutorials/how-to-use-ssh-keys-with-digitalocean-droplets).
These steps are not required, be recommended.

### Log-in into the server (This may require a password in DigitalOcean):

    ssh $USER@$SERVER

### Configure ssh key log-in

- Edit the `.ssh/authorized_keys` file: `vim .ssh/authorized_keys`.
- Add your own ssh public key (It'd be at `~/.ssh/id_rsa.pub` in your local machine).
- Log-out from the server (`exit`) and log-in without password.
- **If it fails**, run the following commands locally and try again:
  - `eval $(ssh-agent -s)`
  - `ssh-add ~/.ssh/id_rsa`

### Disable log-in with password

- Edit the `sshd_config` file: `vim /etc/ssh/sshd_config` in the server.
- Find the line `PermitRootLogin yes` and replace it by: `PermitRootLogin without-password`
- Restart the `ssh` service: `systemctl restart ssh`
- Try to log-in with password, it *must fail*

## Generate the ssh keys

### Generate the ssk keys

- Log-in into the server and run the command: `ssh-keygen -t rsa`
- Copy the content of `.ssh/id_rsa.pub`.
- Paste its content into `.ssh/authorized_keys`

### Give repository access

Go to the "Deploy keys" seccion in Gitlab and add a new key with a descriptive title and the content of `.ssh/id_rsa.pub` as value.

### Give server access

GO to the "Secret Variables" seccion in the CI/CD configuration
Add a variable with the key "SSH_PRIVATE_KEY_TESTING" and its value must be the content of the `.ssh/id_rsa` file.

### Add some required values

At the same seccion "Secret Variables", add the following variables for database configuration:

- `PGUSER_TESTING`
- `PGPASSWORD_TESTING`

### Integrate with `gitlab-ci.yml`.

In the `.gitlab-ci.yml` file, Add the following lines (HOST and USER must be modifided accordingly):

    variables:
      DEPLOY_IMAGE: gitlab.devartis.com:4567/devops/simple-deploy:0.2-alpha
      REPO_URL: git@gitlab.devartis.com:project_group/project.git # Cambiar a tu repo!

    .deploy_template: &deploy_definition
      image: $DEPLOY_IMAGE
      stage: deploy
      script:
        bash entrypoint.sh
      when: manual

    deploy_testing:
      <<: *deploy_definition
      environment: testing
      variables:
        SSH_PRIVATE_KEY: $SSH_PRIVATE_KEY_TESTING
        BRANCH: $CI_BUILD_REF_NAME
        POSTGRES_USER: $PGUSER_TESTING
        POSTGRES_PASSWORD: $PGPASSWORD_TESTING
        HOST: "138.197.72.21" # Replace with your server IP
        USER: "root" # Replace with your privileged user
      only:
        - master


Upload the code to the repository, into the "master" branch. Gitlab will show a button for deploying the application.