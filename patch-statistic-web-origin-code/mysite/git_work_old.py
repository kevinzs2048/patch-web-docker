# -*- coding: utf-8 -*-
# created by Shuai.Zhao Apr.2015

import re
import os,sched
import subprocess
import sys
import MySQLdb
import time,datetime
import types

schedule = sched.scheduler(time.time,time.sleep)

def run(tablename,project_dir, date_from, date_to, search_key,name_list):
    bug_dic = {}
    bug_branch_dic = {}
    try:
        os.chdir(project_dir)
    except Exception, e:
        raise e
    cmd = "git pull"
    os.system(cmd)

    check_all(tablename,name_list)
 
# check for all the people in the list
def check_all(tabelname,name_list):
    for name in name_list:
        get_commit_nums(tabelname,name)
	
# get the number of commits
def get_commit_nums(tablename,name):
    cmd_git_nums = 'git log --author=\"'+name+'\" --pretty=format:\"%h %an %ae %ci   %s. \"'
    print cmd_git_nums
    proc = subprocess.Popen(cmd_git_nums,shell=True,stdout=subprocess.PIPE)
    for line in proc.stdout.readlines():

	match_hash = re.search("\w+",line)
	if match_hash :
	    user_hash = match_hash.group()
            print user_hash
	    
	else:
	    print("Can not match hash")

	match_name = re.search(name, line)
	if match_name :
	    user_name = match_name.group()
            print user_name
	    
	else:
	    print("Can not match name")

#	match_email = re.search('\S*@linux.vnet.ibm.com',line)
#	if match_email:
#	    user_email = match_email.group()
#	    print user_email    
#	else:
#	    print("Can not match useremail")
	user_email = " "

#	Time format    :            2013-05-20 13:14:52
	match_committime = re.search(r'\w+-\w+-\w+ \w+:\w+:\w+',line)
	if match_committime:
	    user_committime = match_committime.group()
	    print user_committime
	else:
	    print("Can not match committime")
	
	match_comment = re.search(r'  .*\. ',line)
	if match_comment:
	    user_comment = match_comment.group()
	    print user_comment
	else:
	    print("Can not match comment")
	if match_name and match_committime and match_comment and match_hash:
            print("Match complete")
	    put_into_mysql(tablename,user_name,user_email,user_committime,user_comment,user_hash)
	
def put_into_mysql(tablename,name,email,committime,comment,hash):
	conn= MySQLdb.connect(
			host='localhost',
			port = 3306,
			user='root',
			passwd='8399633',
			db ='LTC_China_CommitInfo',
			)
	cur = conn.cursor()
	print 'Ongoing writing to the database'
#        time_datetime = datetime.datetime.strptime(committime,'%Y-%m-%d %H:%M:%S')
#	print type(time_datetime)
#	print time_datetime
	sqli="insert into "+tablename+" values(%s,%s,%s,%s,%s,%s)"
	cur.execute(sqli,(' ',name,email,committime,comment,hash))	
	cur.close()
	conn.commit()
	conn.close()

def mysql_init(tablename):
	conn= MySQLdb.connect(
			host='localhost',
			port = 3306,
			user='root',
			passwd='8399633',
			db ='LTC_China_CommitInfo',
			)
	cur = conn.cursor()
#cur.execute("truncate table commitinfo_kernel_project")
	cur.execute("truncate table "+tablename)
	print 'Flush table success:'+tablename
	cur.close()
	conn.commit()
	conn.close()

# analyze log 
def deal_lines(date_from, date_to, search_key, stdout):
    for line in stdout.split('commit '):
        if re.search('Bug: \d+', line) is not None and re.search(search_key, line) is not None:
            bug_id = line.split('Bug: ')[1].split('\n')[0]
            if bug_id not in bug_dic:
                bug_dic[bug_id] = [line]
            else:
                bug_dic[bug_id] += [line]
    return bug_dic

# running in cycle
def update_database(para1,para2,inc):
    schedule.enter(inc,0,update_database,(para1,para2,inc))
    tablename1="commitinfo_kernel_project"
    project_dir1 = "/var/www/mysite/linux-stable/"
    name_list1 = ['Li Zhong','Wei Yang','Jia He','Boqun Feng',]
    mysql_init(tablename1)
    run(tablename1,project_dir1, date_from, date_to, search_key,name_list1)
#    project_dir2 = ""
#    tablename2="commitinfo_zfrobisher_project"
#    msql_init(tablename2)
#    run(tablename2,project_dir2, date_from, date_to, search_key,name_list2)

#   msql_init("")
#   run(project_dir3, date_from, date_to, search_key,name_list3)

# running once
def update_database0(para1,para2,inc):
    tablename1="commitinfo_kernel_project"
    project_dir1 = "/root/linux/"
    name_list1 = ['heijlong','Li Zhong','Wei Yang','Jia He','Boqun Feng','Xiao Guangrong','Mike Qiu','Guo Chao','Wangpeng Li','Zhi Yong Wu','Zheng Huai Cheng','Micheal Wang','Cong Meng','Liu Sheng','Li Zhang']
    mysql_init(tablename1)
    run(tablename1,project_dir1, date_from, date_to, search_key,name_list1)
    
    name_list2 = ['hejianet','Jing Cai','Leno Hou','Shuai Zhao','Qu Jiang']
    project_dir2="/root/zfrobisher-installer"
    tablename2="commitinfo_zfrobisher_project"
    mysql_init(tablename2)
    run(tablename2,project_dir2, date_from, date_to, search_key,name_list2)
    
    name_list3 = ['heijlong','park hei']
    project_dir3="/root/nova"
    tablename3="commitinfo_openstack_project"
    mysql_init(tablename3)
    run(tablename3,project_dir3, date_from, date_to, search_key,name_list3)

#   msql_init("")
#   run(project_dir3, date_from, date_to, search_key,name_list3)

def begin_running(inc=86400):
    schedule.enter(inc,0,update_database0,(0,0,inc))
    schedule.run()

if __name__ == '__main__':
    date_from = "2015-01-25"
    date_to = "2015-02-26"
    search_key = "Bug:\d"
#    name_list = ['Li Zhong']
    update_database0(0,0,0)
    begin_running()


