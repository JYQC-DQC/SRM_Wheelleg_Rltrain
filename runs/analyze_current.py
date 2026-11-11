import sys,getpass
sys.path.insert(0,'runs/ssh_client')
import paramiko
c=paramiko.SSHClient();c.load_host_keys('C:/Users/Dell/.ssh/known_hosts');c.connect('183.147.142.40',port=30108,username='root',password=getpass.getpass('SSH password: '),look_for_keys=False,allow_agent=False,timeout=15)
cmd=r'''cd /root/gpufree-data/wheelleg/scut_current_b1b4dbc
/workspace/isaaclab/_isaac_sim/python.sh -c 'import torch,json,pathlib; p=pathlib.Path("runs/scut_current_resume200"); a=torch.load(p/"model_399.pt",map_location="cpu",weights_only=False); print("CHECKPOINT",a["iter"],"FINITE",all(torch.isfinite(v).all() for v in a["model_state_dict"].values())); print("CURRICULUM",a["infos"]); print("NOISE",{k:v.tolist() for k,v in a["model_state_dict"].items() if "std" in k}); print("PARAMS",(p/"params/run.json").read_text())'
grep -c 'Traceback' /tmp/scut_current_resume200.log
grep -c 'PhysX error' /tmp/scut_current_resume200.log
pgrep -af '[p]ython3 -m isaac.scripts.train'
'''
_,o,e=c.exec_command(cmd);print(o.read().decode());print(e.read().decode());c.close()
