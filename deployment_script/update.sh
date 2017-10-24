#!/usr/bin/env bash
set -e;

login_user=""
inventory=""

usage() {
	echo "Usage: `basename $0`" >&2
	echo "(-l login_user )"; >&2
}
if ( ! getopts "i:l:" opt); then
    usage;
	exit $E_OPTERROR;
fi

while getopts "i:l:" opt;do
	case "$opt" in
	l)
	  login_user="$OPTARG"
      ;;
    i)
	  inventory="$OPTARG"
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

if [ ! "$inventory" ] || [ ! "$login_user" ]
then
    echo "Missing options..."
    usage
    exit 1
fi


extra_vars="ansible_user=$login_user"

echo "INFO: Running tasks with tag: quickly"
ansible-playbook site.yml --extra-vars "$extra_vars" -i "$inventory" --tags "quickly"
