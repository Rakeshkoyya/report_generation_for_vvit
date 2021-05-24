from django.shortcuts import render ,redirect
from django.http import HttpResponse
from django.contrib.auth.models import auth

import pandas as pd
from . models import firstyear,secondyear,thirdyear,fourthyear,count_info
from io import BytesIO

import xlsxwriter

from . import backend

result_df=0
first_df_val=0
filename='report'
date='00'

year_id={'I':firstyear,'II':secondyear,'III':thirdyear,'IV':fourthyear}


def home(request):
	if count_info.objects.all().count()<=0:
		count_info(total_reports=0,id_number=1).save()
	t=count_info.objects.get(id_number=1)
	total=t.total_reports
	students_count=firstyear.objects.all().count()+secondyear.objects.all().count()+thirdyear.objects.all().count()+fourthyear.objects.all().count()

	return render(request,'index.html',{'total':total,'students':students_count})


# Create your views here.
def admin(request):
	if  request.user.is_authenticated:
		return redirect('admin_entry')
	if request.method== 'POST':
		uname=request.POST['username']
		upwd=request.POST['password']
		
	
		user = auth.authenticate(username=uname,password=upwd)

		if user!=None:
			auth.login(request,user)
			return redirect('admin_entry')

		return render(request,'admin_index.html',{'error':"invalid login"})

	return render(request,'admin_index.html')

def givedownload(df,info):
	with BytesIO() as b:
		writer = pd.ExcelWriter(b, engine='xlsxwriter')
		workbook=writer.book
		worksheet=workbook.add_worksheet('Sheet1')
		writer.sheets['Sheet1'] = worksheet
		df.to_excel(writer, sheet_name='Sheet1',startrow=0 , startcol=0)
		writer.save()
		filename = info+'.xlsx'
		response = HttpResponse(
			b.getvalue(),
			content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
		)
		response['Content-Disposition'] = 'attachment; filename=%s' % filename
		return response

def df_by_year(year):
	yeartable=year_id[year]
	students=yeartable.objects.all()
	regdno_list=[i.regd_number for i in students]
	fname_list=[i.full_name for i in students]
	branch_list=[i.branch for i in students]

	return pd.DataFrame({'REGD NO':regdno_list,'FullName':fname_list,'Branch':branch_list})

def import_by_file(stu_file,year):
	table=year_id[year]
	stu_df=pd.read_excel(stu_file,sheet_name=0,engine='openpyxl')
	for i in range(stu_df.shape[0]):
		table(regd_number=stu_df['REGD NO'][i],full_name=stu_df['FullName'][i],branch=stu_df['Branch'][i]).save()
	return


def admin_entry(request):
	if request.user.is_authenticated:
		if request.method=='POST':
			if request.POST['submit_btn'] == 'download1':
				return givedownload(df_by_year('I'),'firstyear_students')
			elif request.POST['submit_btn'] == 'delete1':
				firstyear.objects.all().delete()
				return redirect('admin_entry')
			elif request.POST['submit_btn'] == 'import1':
				stu_file=request.FILES['first_file']
				import_by_file(stu_file,'I')
				return redirect('admin_entry')
			
			elif request.POST['submit_btn'] == 'download2':
				return givedownload(df_by_year('II'),'secondyear_students')
			elif request.POST['submit_btn'] == 'delete2':
				secondyear.objects.all().delete()
				return redirect('admin_entry')
			elif request.POST['submit_btn'] == 'import2':
				stu_file=request.FILES['second_file']
				import_by_file(stu_file,'II')
				return redirect('admin_entry')
			
			elif request.POST['submit_btn'] == 'download3':
				return givedownload(df_by_year('III'),'thirdyear_students')
			elif request.POST['submit_btn'] == 'delete3':
				thirdyear.objects.all().delete()
				return redirect('admin_entry')
			elif request.POST['submit_btn'] == 'import3':
				stu_file=request.FILES['third_file']
				import_by_file(stu_file,'III')
				return redirect('admin_entry')
			
			elif request.POST['submit_btn'] == 'download4':
				return givedownload(df_by_year('IV'),'fourthyear_students')
			elif request.POST['submit_btn'] == 'delete4':
				fourthyear.objects.all().delete()
				return redirect('admin_entry')
			elif request.POST['submit_btn'] == 'import4':
				stu_file=request.FILES['fourth_file']
				import_by_file(stu_file,'IV')
				return redirect('admin_entry')

			return HttpResponse("succesfully completed")

		content={}
		content['firstyear']=firstyear.objects.all().count()
		content['secondyear']=secondyear.objects.all().count()
		content['thirdyear']=thirdyear.objects.all().count()
		content['fourthyear']=fourthyear.objects.all().count()
		return render(request,'admin_entry.html',content)
	return redirect('admin')

def logout(request):
	auth.logout(request)
	return redirect('admin')


def report(request):
	global result_df,first_df_val,filename,date

	if request.method== 'POST':
		subject=request.POST['subject']
		branch=request.POST.get('branch')
		year=request.POST.get('year')
		filter=request.POST.get('filter')
		msfile=request.FILES['msfile']
		msdf=pd.read_csv(msfile,encoding='utf-16',delimiter='\t')

		filename=year+'_'+branch+'_'+subject+'_'

		if 'stfile' in request.FILES:
			stfile=request.FILES['stfile']
			stdf=pd.read_excel(stfile,sheet_name=1,engine='openpyxl')
			result_df,date=backend.get_result_by_stu(stdf,msdf,filter)
		else:
			result_df,date=backend.get_result_by_db(msdf,year,branch,filter)
			
 
		content={}
		# content['unknown']=unknow_names
		col_heads=list(result_df.columns.values)
		content['redgs']=list(result_df.loc[:,'REGD NO'])
		content['names']=list(result_df.loc[:,'FullName'])
		content['attend']=list(result_df.loc[:,col_heads[2]])

		content['zipped']=zip([i for i in range(1,len(content['redgs'])+1)],content['redgs'],content['names'],content['attend'])
		# content['unknown_zip']=zip( [i for i in range(len(content['redgs'])+1,len(content['unknown'])+1)], content['unknown'])
		t=count_info.objects.get(id_number=1)
		t.total_reports +=1
		t.save()
		return render(request,'report.html',content)
	return render(request,'inner.html')

def download(request):
	if request.method == 'POST':
		if request.POST['submit_button'] == 'download':
			global result_df,first_df_val,filename,date
			with BytesIO() as b:
				writer = pd.ExcelWriter(b, engine='xlsxwriter')

				workbook=writer.book
				worksheet=workbook.add_worksheet('Sheet1')
				writer.sheets['Sheet1'] = worksheet
				# worksheet.merge_range('B'+first_df_val+':E'+first_df_val,'ok')
				# print(first_df_val)
				# worksheet.write('B'+first_df_val, 'not in database but present for meeting')

				result_df.to_excel(writer, sheet_name='Sheet1',startrow=0 , startcol=0)
				writer.save()
				filename = filename+date+'.xlsx'
				response = HttpResponse(
					b.getvalue(),
					content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
				)
				response['Content-Disposition'] = 'attachment; filename=%s' % filename
				return response

		else:
			return render(request,'inner.html')
	return HttpResponse('hey im form download function in admin_site')



def help(request):
	return render(request,'help.html')