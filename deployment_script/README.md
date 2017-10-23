# Simple (Django) deploy

With this project you'll be able to deploy [this django application](https://gitlab.devartis.com/samples/django-sample).

## Requirements

- Ansible: `pip install -r requirements.txt`
- SSH client
  - Ubuntu: `apt-get install openssh-client`
  - Arch linux: `pacman -S openssh` ([docs](https://wiki.archlinux.org/index.php/Secure_Shell#OpenSSH))

See the [documentation](docs/index.md)

## Compatibilitymatrix

Tested compatibility between branches of this repository and django-sample

NOTE: When `(master)` is present, it means there's no specific branch or tag. It must be specified a django version, at least.

    simple-deploy       |  django-sample

    master                 master

    0.2-new-hope           (master) - django-1.9

    0.3-rc1-release        (master) - django-1.11.2

## Contribute

- Create a new issue & a new branch.
- Implement your feature/fix.
- Create a merge-request & assign it to someone else
- Remove Docker image from registry after merge (TODO: Avoid this step)

## Release

- Create a new branch with the form "$RELEASE_NUMBER-release"
- Update the documentation
  - `docs/integration.md`: Change the `DEPLOY_IMAGE:` at the `.gitlab-ci.yml` sample
  - `.gitlab-ci.yml.sample`: Change the `DEPLOY_IMAGE:`.
  - Add an entry at "compatibility matriz"
- Notify!



## Vagrant & Tests

You can test this project using [Vagrant](https://www.vagrantup.com/):

    export REPO_URL=git@gitlab.devartis.com:samples/django-sample.git
    eval "$(ssh-agent -s) # These two lines allow to pull the project with you ssh keys from gitlab
    ssh-add ~/.ssh/id_rsa
    vagrant up --provision # Setup and run playbook