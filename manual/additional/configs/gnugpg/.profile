if test -f $HOME/.gpg-agent-info && kill -0 `cut -d: -f 2 $HOME/.gpg-agent-info` 2> /dev/null; then
	GPG_AGENT_INFO=`cat $HOME/.gpg-agent-info`
	export GPG_AGENT_INFO
else
	eval `gpg-agent --daemon --write-env-file ~/.gpg-agent-info`
fi

if [ -f "${HOME}/.gpg-agent-info" ]; then
	. "${HOME}/.gpg-agent-info"
	export GPG_AGENT_INFO
	export SSH_AUTH_SOCK
	export SSH_AGENT_PID
fi
