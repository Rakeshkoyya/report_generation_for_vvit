import pandas as pd
from datetime import date, datetime

import re

from .models import firstyear,secondyear,thirdyear,fourthyear

year_id={'I':firstyear,'II':secondyear,'III':thirdyear,'IV':fourthyear}

year_p={'17':'IV','18':'III','19':'II','20':'I'}

def get_time_details(df):
	maxd=mind=datetime.strptime(df.loc[0,'Timestamp'],'%m/%d/%Y, %I:%M:%S %p')
	for i in df['Timestamp']:
		maxd=max(maxd,datetime.strptime(i,'%m/%d/%Y, %I:%M:%S %p'))
		mind=min(mind,datetime.strptime(i,'%m/%d/%Y, %I:%M:%S %p'))
	total_time=(maxd-mind)

	date_head=maxd.strftime('%d-%m-%Y')
	time_head='time['+maxd.strftime('%d/%m')+']'

	return total_time,date_head,time_head,maxd


def get_result(regdno_list,fname_list,msdf,filter):
	duration_list=[0 for _ in range(len(regdno_list))]
	attend_list=[0 for _ in range(len(regdno_list))]

	visited_nameformfile=[]
	unknown_name_list=[]
	unknown_duration_list=[]
	unknown_attend_list=[]

	total_time,date_head,time_head,maxd=get_time_details(msdf)

	import datetime as datetm

	# calculating duration
	def cal_duration(periods):
		periods=sorted(periods,key=lambda x:x[1])
		t_time=datetm.timedelta(0)
		pres_time=periods[0][1]
		left=False
		for x in periods:
			if 'Joined' in x[0] and left:
				pres_time=x[1]
				left=False
			elif x[0]=='Left':
				t_time+=x[1]-pres_time
				pres_time=maxd
				left=True
		t_time+=maxd-pres_time
		return t_time

	attendees_dict={}
	for i in msdf.index:
		name=msdf.loc[i,'Full Name']
		time=datetime.strptime(msdf.loc[i,'Timestamp'],'%m/%d/%Y, %I:%M:%S %p')
		data_tup=(msdf.loc[i,'User Action'],time)
		if name in attendees_dict:
			attendees_dict[name].append(data_tup)
		else:
			attendees_dict[name]=[data_tup]

	present_count=0
	absent_count=0

	for i in range(len(regdno_list)):
		t_name,t_regd=fname_list[i],regdno_list[i]


		for index in msdf.index:
			nameformfile=msdf.loc[index,'Full Name']
			
			if t_name.lower() in nameformfile.lower() or t_regd.lower() in nameformfile.lower():
				attend_list[i]='P'
				visited_nameformfile.append(nameformfile)

				t_time=cal_duration(attendees_dict[nameformfile])
				duration_list[i]=str(t_time.seconds//60)+'mins'

				present_count+=1

				break
		else:
			attend_list[i]='A'
			duration_list[i]='0 mins'
			absent_count+=1

	for index in msdf.index:
		if msdf.loc[index,'Full Name'] not in visited_nameformfile:
			nameformfile=msdf.loc[index,'Full Name']
			unknown_name_list.append(nameformfile)
			t_time=cal_duration(attendees_dict[nameformfile])
			unknown_duration_list.append(str(t_time.seconds//60)+'mins')
			unknown_attend_list.append('*P')
			visited_nameformfile.append(nameformfile)


	resdf=pd.DataFrame({'REGD NO': regdno_list,'FullName':fname_list, date_head:attend_list, 
	time_head:duration_list, 'Person':['Student' for _ in range(len(regdno_list))]})

	col1=[' ' for _ in range(len(unknown_name_list))]+['RESULTS']
	col2=[i for i in unknown_name_list]+['Present: '+str(present_count)]
	col3=[i for i in unknown_attend_list]+['Absent: '+str(absent_count)]
	col4=[i for i in unknown_duration_list]+['class dur:'+str(total_time)]
	undf=pd.DataFrame({'REGD NO': col1 ,'FullName':col2, date_head:col3, 
	time_head:col4,'Person':['Teacher/Unknown' for _ in range(len(col1)-1)]+['unknown count:'+str(len(unknown_name_list))]})

	finaldf=pd.concat([resdf,undf],ignore_index=True)
	
	return finaldf,date_head



def get_result_by_db(msdf,year,branch,filter):
	table=year_id[year]
	students=table.objects.filter(regd_number__regex=r'......'+branch+'..')
	regdno_list=[i.regd_number for i in students]
	# fname_list=[i.full_name for i in students]

	return get_result(regdno_list,msdf,filter)


def get_result(regdno_list,msdf,filter):
	duration_list=[0 for _ in range(len(regdno_list))]
	attend_list=[0 for _ in range(len(regdno_list))]

	visited_nameformfile=[]
	unknown_name_list=[]
	unknown_duration_list=[]
	unknown_attend_list=[]

	total_time,date_head,time_head,maxd=get_time_details(msdf)

	import datetime as datetm

	# calculating duration
	def cal_duration(periods):
		periods=sorted(periods,key=lambda x:x[1])
		t_time=datetm.timedelta(0)
		pres_time=periods[0][1]
		left=False
		for x in periods:
			if 'Joined' in x[0] and left:
				pres_time=x[1]
				left=False
			elif x[0]=='Left':
				t_time+=x[1]-pres_time
				pres_time=maxd
				left=True
		t_time+=maxd-pres_time
		return t_time

	attendees_dict={}
	for i in msdf.index:
		name=msdf.loc[i,'Full Name']
		time=datetime.strptime(msdf.loc[i,'Timestamp'],'%m/%d/%Y, %I:%M:%S %p')
		data_tup=(msdf.loc[i,'User Action'],time)
		if name in attendees_dict:
			attendees_dict[name].append(data_tup)
		else:
			attendees_dict[name]=[data_tup]

	present_count=0
	absent_count=0

	for i in range(len(regdno_list)):
		t_regd=regdno_list[i]


		for index in msdf.index:
			nameformfile=msdf.loc[index,'Full Name']
			
			if t_regd.lower() in nameformfile.lower():
				attend_list[i]='P'
				visited_nameformfile.append(nameformfile)

				t_time=cal_duration(attendees_dict[nameformfile])
				duration_list[i]=str(t_time.seconds//60)+'mins'

				present_count+=1

				break
		else:
			attend_list[i]='A'
			duration_list[i]='0 mins'
			absent_count+=1

	for index in msdf.index:
		if msdf.loc[index,'Full Name'] not in visited_nameformfile:
			nameformfile=msdf.loc[index,'Full Name']
			unknown_name_list.append(nameformfile)
			t_time=cal_duration(attendees_dict[nameformfile])
			unknown_duration_list.append(str(t_time.seconds//60)+'mins')
			unknown_attend_list.append('*P')
			visited_nameformfile.append(nameformfile)


	resdf=pd.DataFrame({'REGD NO': regdno_list, date_head:attend_list, 
	time_head:duration_list, 'Person':['Student' for _ in range(len(regdno_list))]})

	col1=[' ' for _ in range(len(unknown_name_list))]
	col2=[i for i in unknown_name_list]+['RESULTS']
	col3=[i for i in unknown_attend_list]+['P: '+str(present_count)+'|A: '+str(absent_count)]
	col4=[i for i in unknown_duration_list]+['class dur:'+str(total_time)]

	undf=pd.DataFrame({'REGD NO': col2 , date_head:col3, 
	time_head:col4,'Person':['Teacher/Unknown' for _ in range(len(col1))]+['unknown count:'+str(len(unknown_name_list))]})

	finaldf=pd.concat([resdf,undf],ignore_index=True)
	
	return finaldf,date_head



def get_result_by_stu(stdf,msdf,filter):
	regdno_list=list(stdf.loc[:,'REGD NO'])
	# fname_list=list(stdf.loc[:,'FullName'])

	return get_result(regdno_list,msdf,filter)

	

	
def predict(df):
	mat=[]
	for i in df.index:
		pat=r'[0-9][0-9][A-Z][A-Z][0-9][A-Z][0-9][0-9]..'
		mat+=re.findall(pat,df.loc[i,'Full Name'])
		
	count_dic={}
	brach_dic={}
	
	for i in mat:
		y=i[:2];x=i[6:8]
		count_dic[y]=count_dic[y]+1 if y in count_dic else 1
		brach_dic[x]=brach_dic[x]+1 if y in brach_dic else 1
	
	year=max(count_dic, key=count_dic.get)
	branch=max(brach_dic, key=brach_dic.get)


	return year_p[year],branch


def check_msdf(msdf):
	col_heads=list(msdf.columns)
	if 'Full Name' in col_heads and 'User Action' in col_heads and 'Timestamp' in col_heads:
		return True 
	return False

def check_df(df):
	col_heads=list(df.columns)
	if 'REGD NO' in col_heads:
		return True 
	return False

