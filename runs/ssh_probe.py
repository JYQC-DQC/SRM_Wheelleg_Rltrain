import sys,getpass
sys.path.insert(0,'runs/ssh_client')
import paramiko
c=paramiko.SSHClient(); c.load_system_host_keys(); c.load_host_keys('C:/Users/Dell/.ssh/known_hosts')
c.connect('183.147.142.40',port=30108,username='root',password=getpass.getpass('SSH password: '),look_for_keys=False,allow_agent=False,timeout=15)
_,o,e=c.exec_command('pwd; pgrep -af "[p]ython3 -m isaac.scripts.train"; ls -lt /root/gpufree-data/wheelleg/scut_latest_framework/runs/scut_latest_smoke512_v2/model_*.pt | head -n 2')
print(o.read().decode());print(e.read().decode());c.close()
