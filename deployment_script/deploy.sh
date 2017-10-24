#!/usr/bin/env bash
set -e;

postgresql_user=""
postgresql_password=""
login_user=""
inventory=""
update=""

usage() {
	echo "Usage: `basename $0`" >&2
    echo "(-i inventory )"; >&2
	echo "(-p postgresql db user) (-P postgresql db password)" >&2
	echo "(-l login_user )[-u]"; >&2
}
if ( ! getopts "p:i:P:l:u" opt); then
    usage;
	exit $E_OPTERROR;
fi

while getopts "p:i:P:l:u" opt;do
	case "$opt" in
	p)
	  postgresql_user="$OPTARG"
      ;;
    i)
	  inventory="$OPTARG"
      ;;
	P)
	  postgresql_password="$OPTARG"
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

if [ ! "$login_user" ] || [ ! "$postgresql_user" ] || [ ! "$postgresql_password" ] || [ ! "$inventory" ]
then
    echo "Missing options..."
    usage
    exit 1
fi


extra_vars="ansible_user=$login_user \
        postgresql_user=$postgresql_user \
        postgresql_password=$postgresql_password"

if [ -z "$update" ]; then
    ansible-playbook site.yml --extra-vars "$extra_vars" -i "$inventory" -vvv
else
    echo "INFO: Running tasks with tag: quickly"
    ansible-playbook site.yml --extra-vars "$extra_vars" -i "$inventory" --tags "quickly" -vvv
fi
