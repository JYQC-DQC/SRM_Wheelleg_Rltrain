import sys,getpass,pathlib
sys.path.insert(0,'runs/ssh_client')
import paramiko
c=paramiko.SSHClient();c.load_host_keys('C:/Users/Dell/.ssh/known_hosts');c.connect('183.147.142.40',port=30108,username='root',password=getpass.getpass('SSH password: '),look_for_keys=False,allow_agent=False,timeout=15)
s=c.open_sftp();out=pathlib.Path('runs/ppo_diagnosis');out.mkdir(exist_ok=True)
base='/workspace/isaaclab/_isaac_sim/kit/python/lib/python3.11/site-packages/rsl_rl/'
for f in ['algorithms/ppo.py','runners/on_policy_runner.py','storage/rollout_storage.py','modules/actor_critic.py']:
 s.get(base+f,str(out/f.replace('/','_')))
s.get('/workspace/isaaclab/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py',str(out/'vecenv_wrapper.py'))
s.close();print('SOURCES_DOWNLOADED',flush=True)
while True:
 line=input('ACTION> ')
 if line=='quit':break
 if line.startswith('put '):
  a,b=line[4:].split('|'); s=c.open_sftp();s.put(a,b);s.close();print('UPLOADED',flush=True)
 elif line.startswith('get '):
  a,b=line[4:].split('|');s=c.open_sftp();s.get(a,b);s.close();print('DOWNLOADED',flush=True)
 else:
  _,o,e=c.exec_command(line);print(o.read().decode(),flush=True);print(e.read().decode(),flush=True)
c.close()
