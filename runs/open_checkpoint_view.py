import sys,getpass
sys.path.insert(0,'runs/ssh_client')
import paramiko
c=paramiko.SSHClient();c.load_host_keys('C:/Users/Dell/.ssh/known_hosts');c.connect('183.147.142.40',port=30108,username='root',password=getpass.getpass('SSH password: '),look_for_keys=False,allow_agent=False,timeout=15)
s=c.open_sftp();s.put('runs/play_latest_checkpoint.py','/root/gpufree-data/wheelleg/scut_current_b1b4dbc/runs/play_latest_checkpoint.py');s.close()
cmd=r'''cd /root/gpufree-data/wheelleg/scut_current_b1b4dbc
pgrep -af '[p]ython3 -m isaac.scripts.train' || true
nohup env DISPLAY=:20 XAUTHORITY=/home/ubuntu/.Xauthority PYTHONUNBUFFERED=1 /workspace/isaaclab/_isaac_sim/python.sh runs/play_latest_checkpoint.py > /tmp/scut_checkpoint_view.log 2>&1 < /dev/null &
echo VIEW_PID=$!
'''
_,o,e=c.exec_command(cmd);print(o.read().decode());print(e.read().decode());c.close()
