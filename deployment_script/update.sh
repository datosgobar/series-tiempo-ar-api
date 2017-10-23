#!/usr/bin/env bash
set -e;

repo_url=""
checkout_branch=""
host=""
login_user=""

usage() {
	echo "Usage: `basename $0`" >&2
	echo "(-r repository_url)" >&2
	echo "(-b checkout branch)" >&2
	echo "(-h host to be provisioned) (-l login_user )"; >&2
}
if ( ! getopts "r:s:b:h:l:" opt); then
    usage;
	exit $E_OPTERROR;
fi

while getopts "r:s:b:h:l:" opt;do
	case "$opt" in
	r)
	  repo_url="$OPTARG"
      ;;
	b)
	  checkout_branch="$OPTARG"
      ;;
	h)
	  host="$OPTARG"
      ;;
	l)
	  login_user="$OPTARG"
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

if [ ! "$repo_url" ] || [ ! "$checkout_branch" ]  || [ ! "$host" ] || [ ! "$login_user" ]
then
    echo "Missing options..."
    usage
    exit 1
fi


extra_vars="application_clone_url=$repo_url \
        checkout_branch=$checkout_branch \
        ansible_ssh_user=$login_user"

echo "INFO: Running tasks with tag: quickly"
ansible-playbook site.yml --extra-vars "$extra_vars" -i "$host," --tags "quickly"
