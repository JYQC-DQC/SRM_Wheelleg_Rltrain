import sys,getpass
sys.path.insert(0,'runs/ssh_client')
import paramiko
c=paramiko.SSHClient();c.load_host_keys('C:/Users/Dell/.ssh/known_hosts');c.connect('183.147.142.40',port=30108,username='root',password=getpass.getpass('SSH password: '),look_for_keys=False,allow_agent=False,timeout=15)
cmd=r'''cd /root/gpufree-data/wheelleg/scut_current_b1b4dbc
 tail -n 10 /tmp/scut_original_4096_5000.log
 pgrep -af '[p]ython3 -m isaac.scripts.train' || true
 ls -lt runs/scut_original_4096_5000/model_*.pt | head -n 3
'''
_,o,e=c.exec_command(cmd);print(o.read().decode());print(e.read().decode());c.close()
