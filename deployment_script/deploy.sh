#!/usr/bin/env bash
set -e;

repo_url=""
checkout_branch=""
postgresql_user=""
postgresql_password=""
host=""
login_user=""
update=""

usage() {
	echo "Usage: `basename $0`" >&2
	echo "(-r repository_url) (-b checkout branch)" >&2
	echo "(-p postgresql db user) (-P postgresql db password)" >&2
	echo "(-h host to be provisioned) (-l login_user )[-u]"; >&2
}
if ( ! getopts "r:b:p:P:h:l:u" opt); then
    usage;
	exit $E_OPTERROR;
fi

while getopts "r:b:p:P:h:l:u" opt;do
	case "$opt" in
	r)
	  repo_url="$OPTARG"
      ;;
	b)
	  checkout_branch="$OPTARG"
      ;;
	p)
	  postgresql_user="$OPTARG"
      ;;
	P)
	  postgresql_password="$OPTARG"
      ;;
	h)
	  host="$OPTARG"
      ;;
	l)
	  login_user="$OPTARG"
      ;;
	u)
	  update="1"
      ;;
	\?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
	esac
done

if [ ! "$repo_url" ] || [ ! "$host" ] || [ ! "$login_user" ] \
    || [ ! "$checkout_branch" ] || [ ! "$postgresql_user" ] || [ ! "$postgresql_password" ]
then
    echo "Missing options..."
    usage
    exit 1
fi


extra_vars="application_clone_url=$repo_url \
        checkout_branch=$checkout_branch \
        ansible_ssh_user=$login_user \
        postgresql_user=$postgresql_user \
        postgresql_password=$postgresql_password"

if [ -z "$update" ]; then
    ansible-playbook site.yml --extra-vars "$extra_vars" -i "$host," -vvv
else
    echo "INFO: Running tasks with tag: quickly"
    ansible-playbook site.yml --extra-vars "$extra_vars" -i "$host," --tags "quickly" -vvv
fi
