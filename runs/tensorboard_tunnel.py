import sys,getpass,socket,threading,select,time
sys.path.insert(0,'runs/ssh_client')
import paramiko
c=paramiko.SSHClient();c.load_host_keys('C:/Users/Dell/.ssh/known_hosts');c.connect('183.147.142.40',port=30108,username='root',password=getpass.getpass('SSH password: '),look_for_keys=False,allow_agent=False,timeout=15)
c.get_transport().set_keepalive(30)
server=socket.socket(); server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); server.bind(('127.0.0.1',16007));server.listen(20)
def proxy(sock):
 channel=c.get_transport().open_channel('direct-tcpip',('127.0.0.1',6007),sock.getpeername())
 try:
  while True:
   ready,_,_=select.select([sock,channel],[],[],30)
   for source in ready:
    data=source.recv(65536)
    if not data:return
    (channel if source is sock else sock).sendall(data)
 finally:channel.close();sock.close()
print('TUNNEL_READY http://127.0.0.1:16007',flush=True)
while True:
 sock,_=server.accept();threading.Thread(target=proxy,args=(sock,),daemon=True).start()
