import time, json

def backup_lists(already,already_time,out_time,left_for_today):
    print('Backing up data...')
    file_writer = open('pending.log','w')
    file_writer.write(str(already)+'|'+str(already_time)+'|'+str(out_time)+'|'+str(left_for_today))
    file_writer.close()

def restore_lists(already,already_time,out_time,left_for_today):
    file_reader = open('pending.log','r')
    dumped_string = file_reader.readline()
    dumped_string=dumped_string.replace("'",'"')
    already,already_time,out_time,left_for_today = dumped_string.split('|',4)
    already = json.loads(already)
    already_time = json.loads(already_time)
    out_time = json.loads(out_time)
    left_for_today = json.loads(left_for_today)
    
    return already,already_time,out_time,left_for_today
