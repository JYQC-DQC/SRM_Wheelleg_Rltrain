import sys,getpass
sys.path.insert(0,'runs/ssh_client')
import paramiko
c=paramiko.SSHClient();c.load_host_keys('C:/Users/Dell/.ssh/known_hosts');c.connect('183.147.142.40',port=30108,username='root',password=getpass.getpass('SSH password: '),look_for_keys=False,allow_agent=False,timeout=15)
_,o,e=c.exec_command('tail -n 20 /tmp/scut_checkpoint_view.log; pgrep -af "[p]lay_latest_checkpoint.py"')
print(o.read().decode());print(e.read().decode());c.close()
