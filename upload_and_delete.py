#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import os.path
import boto3

def check_if_exist(bucket,key):
    s3 = boto3.resource('s3')
    try:
        s3.Object(bucket, key).e_tag
        return True
    except:
        return False

def delete_file(bucket):
    # instance_info = os.popen("ec2-metadata -i").read() #instance-id: i-00388231727f8b402
    # instance_id = instance_info[instance_info.find('i-')+2:] #'00388231727f8b402'
    instance_id = get_id()
    all_plot_lists = os.popen('ls /home/*/*.plot').read().strip().split('\n')
    for plot in all_plot_lists:
        if check_if_exist(bucket,plot.replace('/home',instance_id.strip())):
            os.system('sudo rm '+plot)  
            
def get_id():
    r = os.popen('curl "http://metadata.google.internal/computeMetadata/v1/instance/id" -H "Metadata-Flavor: Google"').read()
    print(r)
    return r
    

def aws_s3_sync(bucket):
    r = os.popen("ps -ef |grep 'aws s3 sync'").read()
    # instance_info = os.popen("ec2-metadata -i").read() #instance-id: i-00388231727f8b402
    # instance_id = instance_info[instance_info.find('i-')+2:] #'00388231727f8b402'
    instance_id = get_id()
    print(r)
    #nvme = """nvme list --output-format=json | jq -r '.Devices' | jq -r 'map(select(.ModelNumber=="Amazon EC2 NVMe Instance Storage")) | .[].DevicePath'"""
    #nvme_lists = os.popen(nvme).read()  
    #number = len(nvme_lists.split())   #n=1 to 8
    number = 2
    
    for i in range(number):
        if '/chia'+str(i+1)+'/' not in r:
            os.system('nohup aws s3 sync --storage-class ONEZONE_IA /home/chia'+str(i+1)+'/ s3://'+bucket+'/'+instance_id.strip()+'/chia'+str(i+1)+'/' +' --exclude "*" --include "*.plot" &')

    #os.system('sudo mkdir /home/qiya/'+str(instance_id))

def get_number_in_s3_folder(bucket,prefix):
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(bucket)
    
    #get all lists
    all_list = (i for i in s3_bucket.objects.filter(Prefix=prefix)) #instance_id.strip()+'/chia'+str(n)+'/')
    
    #calculate number
    count = 0
    try:
        while True:
            obj = next(all_list)
            print(count)
            if obj.key[-4:] == 'plot':
                count += 1
            #if count >=600:
                #break
    except Exception as e:
        print(e)
    print('count',count)
    return count
    

def shutdown(bucket,rounds,r_times):

    #nvme = """nvme list --output-format=json | jq -r '.Devices' | jq -r 'map(select(.ModelNumber=="Amazon EC2 NVMe Instance Storage")) | .[].DevicePath'"""
    #nvme_lists = os.popen(nvme).read()  
    #number = len(nvme_lists.split())   #n=1 to 8
    number = 2
    plots_times = r_times  #eg. 7次并发
    rounds = rounds #1轮
    
    # instance_info = os.popen("ec2-metadata -i").read() #instance-id: i-00388231727f8b402
    # instance_id = instance_info[instance_info.find('i-')+2:] #'00388231727f8b402'
    instance_id = get_id()
    
    sum_plots = 0
    for n in range(number): #eg. n = 0 and 1
        sum_plots += get_number_in_s3_folder(bucket,instance_id.strip()+'/chia'+str(n)+'/')
        print('sum_plots:',sum_plots)
    if sum_plots >= int(plots_times)*int(number)*int(rounds):
        os.system('sudo shutdown')

if __name__ == '__main__':
    try:
        argv = sys.argv[1:]
        for i, options in enumerate(argv):
            if options in ("-bucket","-b","--b"):
                bucket = argv[i+1]
            #if options in ("-n"):
                #rounds = argv[i+1]
            if options in ("-r"): #默认7
                r_times = argv[i+1]
        print('your bucket:',bucket)
        #print('your round:',rounds)
        print('your bingfa:',r_times)
        #shutdown(bucket,1,r_times)  不知道什么鬼功能，先关了
        delete_file(bucket)
        aws_s3_sync(bucket)
    except Exception as e:
        print(e)