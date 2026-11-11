import sys,getpass
sys.path.insert(0,'runs/ssh_client')
import paramiko
c=paramiko.SSHClient();c.load_host_keys('C:/Users/Dell/.ssh/known_hosts');c.connect('183.147.142.40',port=30108,username='root',password=getpass.getpass('SSH password: '),look_for_keys=False,allow_agent=False,timeout=15)
s=c.open_sftp();s.put('config/reference/scut_p1.yaml','/root/gpufree-data/wheelleg/scut_current_b1b4dbc/config/reference/scut_p1_speed14_yaw3.yaml');s.close()
cmd=r'''set -eu
cd /root/gpufree-data/wheelleg/scut_current_b1b4dbc
export PYTHONPATH="$PWD"
P=/workspace/isaaclab/_isaac_sim/python.sh
if pgrep -f '^[^ ]*/python3 -m isaac.scripts.train' >/dev/null; then echo EXISTING_TRAINING_FOUND; exit 2; fi
$P -c 'import torch,pathlib,json; r=pathlib.Path("runs/scut_current_resume200"); p=r/"model_399.pt"; a=torch.load(p,map_location="cpu",weights_only=False); assert a["iter"]==399; assert all(torch.isfinite(v).all() for v in a["model_state_dict"].values()); print("RESUME_ITER",a["iter"],"CURRICULUM",a["infos"])'
nohup env PYTHONUNBUFFERED=1 "$P" -m isaac.scripts.train --task p1-flat --robot runs/scut_current_resume200/params/robot.yaml --policy config/reference/scut_p1_speed14_yaw3.yaml --resume runs/scut_current_resume200/model_399.pt --run-name scut_speed14_yaw3_4096_5000 --num-envs 4096 --iterations 5000 --headless > /tmp/scut_speed14_yaw3_4096_5000.log 2>&1 < /dev/null &
echo TRAIN_PID=$!
if ! ss -ltn | grep -q ':6007 '; then
 nohup "$P" -m tensorboard.main --logdir "$PWD/runs" --port 6007 --host 127.0.0.1 > /tmp/scut_current_tensorboard.log 2>&1 < /dev/null &
 echo TB_PID=$!
fi
'''
_,o,e=c.exec_command(cmd,timeout=90);print(o.read().decode());print(e.read().decode());print('EXIT',o.channel.recv_exit_status());c.close()
