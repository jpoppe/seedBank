import subprocess
import logging
import fcntl

def _shell_escape(command):                                                     
    """escape quotes, backticks and dollar signs"""                             
    for char in ('"', '$', '`'):                                                
        command = command.replace(char, '\%s' % char)                           
    return command     

def run(command, user=None, host=None):                                         
    """run a local or remote command via SSH"""                                 
    if user and host:                                                           
        command = _shell_escape(command)                                        
        proc = subprocess.Popen(['ssh', '-o PasswordAuthentication=no', '%s@%s' 
            % (user, host), 'bash -c "%s"' % command], stdout=subprocess.PIPE)  
    else:                                                                       
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)    
        logging.info('running "%s"', command)                                   
    print 'hoi'
    return proc.stdout.read()

run('sudo ./seedbank.py net -M 52:54:c0:a8:14:65 -o minion -a repository minion001.a.c.m.e debian-squeeze-amd64')

fcntl.fcntl(
    proc.stdout.fileno(),
    fcntl.F_SETFL,
    fcntl.fcntl(proc.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
)

#and then using select to test if the data is ready

while proc.poll() == None:
    readx = select.select([proc.stdout.fileno()], [], [])[0]
    if readx:
        chunk = proc.stdout.read()
        print chunk
