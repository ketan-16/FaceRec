import time, json

already=[]
already_time = []
out_time = []
a = []
at = []
ot = []

def backup_lists(already,already_time,out_time):
    print('Backing up data...')
    file_writer = open('pending.log','w')
    file_writer.write(str(already)+'|'+str(already_time)+'|'+str(out_time))

def restore_lists(already,already_time,out_time):
    file_reader = open('pending.log','r')
    dumped_string = file_reader.readline()
    dumped_string=dumped_string.replace("'",'"')
    a,at,ot = dumped_string.split('|',3)
    already = json.loads(a)
    already_time = json.loads(at)
    out_time = json.loads(ot)
    return already,already_time,out_time
