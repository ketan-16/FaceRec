from flask import Flask
from flask_restful import Resource,Api
from flask_pymongo import PyMongo
from flask_cors import CORS
import time
import smtplib,ssl
import random
from datetime import datetime,date
import csv
import re
app =  Flask(__name__)
CORS(app)
app.config["MONGO_URI"]="mongodb://localhost:27017/staff"
mongo=PyMongo(app)
api = Api(app) 

class Early(Resource):
	def get(self,date1):
		records = mongo.db.attendance.find({"date":date1,"in": { "$ne": 0.0 }})
		records1 = mongo.db.user.find({},{"id":1,"name":1,"_id":0})
		records1 = list(records1)
		date1 = date1.split('-')
		present = []
		records = list(records)
		for rec in records:
			start = time.strftime("%Y %m %d %H %M %S", time.localtime(rec['in']))
			start = start.split()
			start = datetime(int(start[0]),int(start[1]),int(start[2]),int(start[3]),int(start[4]),int(start[5]))
			ten_am = datetime(int(date1[0]),int(date1[1]),int(date1[2]),10,10,00)
			if start <= ten_am:
				rec["_id"] = str(rec["_id"])
				for rec1 in records1:
					if rec['id']==rec1['id']:
						rec['name'] = rec1['name']
						present.append(rec)
		if present:
			return present,200
		else:
			return {'Message':'No such entry found!!'},404

class Late(Resource):
	def get(self,date1):
		records = mongo.db.attendance.find({"date":date1,"in": { "$ne": 0.0 }})
		records = list(records)
		absent = []
		records1 = mongo.db.user.find({},{"id":1,"name":1,"_id":0})
		records1 = list(records1)
		date1 = date1.split('-')
		for rec in records:
			start = time.strftime("%Y %m %d %H %M %S", time.localtime(rec['in']))
			start = start.split()
			start = datetime(int(start[0]),int(start[1]),int(start[2]),int(start[3]),int(start[4]),int(start[5]))
			ten_am = datetime(int(date1[0]),int(date1[1]),int(date1[2]),10,10,00)
			if start > ten_am:
				rec["_id"] = str(rec["_id"])
				for rec1 in records1:
					if rec['id']==rec1['id']:
						rec['name'] = rec1['name']
						absent.append(rec)
		if absent:		
			return absent,200
		else:
			return {'Message':'No such entry found!!'},404

class AddUser(Resource):
	def post(self,id,name,branch,phone,mail,img):
		# records1 = mongo.db.user.find({},{"name":1,"_id":0})
		# records1 = list(records1)
		# for rec1 in records1:
		# 	if rec1['id']==id:
		# 		return {"message":"UserID already exist!!"},400	
		x = mongo.db.user.insert_one({"id":id,"name":name,"branch":branch,"phone":phone,"mail":mail,"isdeleted":False,"img":img})
		if x:
			return {"message":"New User added successfully!!"},201
		else:
			return {"message":"Something went wrong!!"},404

class LastOne(Resource):
	def get(self):
		records = mongo.db.user.find({},{"id":1,"_id":0}).sort("id", -1).limit(1)
		records = list(records)
		for rec in records:
			a = rec['id']
		return {"id":a},200

class AddAttendance(Resource):
	def post(self,name,tim):
		records = mongo.db.user.find_one({"name":name},{"id":1,"_id":0})
		id = records['id']
		dat = time.strftime("%Y-%m-%d", time.localtime(tim))
		record = mongo.db.attendance.find_one({"$and":[{"id":id},{"date":dat}]})
		
		if record["flag"]==0:
			myquery = {"id":id}
			newvalues = { "$set": { "in": tim ,"flag":1} }
			mongo.db.attendance.update_one(myquery, newvalues)
			return {"message":"Attendance updated successfully in !!"},201

		elif record["flag"]==1:
			myquery = {"id":id}
			newvalues = { "$set": { "out": tim ,"flag":2} }
			mongo.db.attendance.update_one(myquery, newvalues)
			return {"message":"Attendance updated successfully out!!"},201
		
		else:
			return {"message":"Logged Out Already"},406

class Forgot(Resource):
	def get(self,mail):
		records = mongo.db.OTP.find({},{"id":1,"_id":0}).sort("id", -1).limit(1)
		records = list(records)
		for rec in records:
			a = rec['id']
		value = random.randint(100000,999999)
		mongo.db.OTP.insert_one({"id":a+1,"otp":value})
		context = ssl.create_default_context()
		with smtplib.SMTP_SSL('smtp.gmail.com',465, context=context) as smtp:
			smtp.login('masntatu@gmail.com','mstt@12??')
			subject = 'Forgot Password'
			body = 'Your Code is {}\nThank you!'.format(value)
			msg= 'Subject: {} \n\n {}'.format(subject,body)
			smtp.sendmail('masntatu@gmail.com',mail,msg)
		return {"Message":"OTP sent successfully!!"}###


class DailyEntry(Resource):
	def get(self):
		members=mongo.db.user.find()
		records = mongo.db.attendance.find({},{"date":1,"_id":0}).sort("date", -1).limit(1)
		records = list(records)
		records = records[0]['date']
		if (records==str(date.today())):
			return {"Message":"Already Updated!!!"}
		for member in members:
			id=member["id"]
			Date=str(date.today())
			data={"id":id,"date":Date,"in":0.0,"out":0.0,"isforced":False,"flag":0}
			mongo.db.attendance.insert_one(data)

		return {"Message":"Daily entry successfully Added!!!"},201  

class MonthWiseAttendance(Resource):
	def get(self,month,year):
		rgx = re.compile('.*{}-{}-.*'.format(year,month))
		records = mongo.db.attendance.find({"date":rgx})
		records = list(records)
		for rec in records:
			rec["_id"] = str(rec["_id"])
		if records:
			return records,200
		else:
			return {"Message":"No such record found!!"},404

class UserWiseAllAttendance(Resource):
	def get(self,name):
		records = mongo.db.user.find_one({"name":name},{"id":1,"_id":0})
		id = records['id']
		records = mongo.db.attendance.find({"id":id})
		records = list(records)
		for rec in records:
			rec["_id"] = str(rec["_id"])
		if records:
			return records,200
		else:
			return {"Message":"No such record found!!"},404

class UserWiseMonthAttendance(Resource):
	def get(self,name,month,year):
		records = mongo.db.user.find_one({"name":name},{"id":1,"_id":0})
		id = records['id']
		rgx = re.compile('.*{}-{}-.*'.format(year,month))
		records = mongo.db.attendance.find({"id":id,"date":rgx})
		records = list(records)
		for rec in records:
			rec["_id"] = str(rec["_id"])
		if records:
			return records,200
		else:
			return {"Message":"No such record found!!"},404

class BranchWiseAllAttendance(Resource):
	def get(self,branch):
		records = mongo.db.user.find({"branch":branch},{"id":1,"_id":0})
		records = list(records)
		idlist = []
		for rec in records:
			idlist.append(rec['id'])
		total_records = []
		for id in idlist:
			records = mongo.db.attendance.find({"id":id})
			records = list(records)
			for rec in records:
				rec["_id"] = str(rec["_id"])
			total_records.extend(records)

		if total_records:
			return total_records,200
		else:
			return {"Message":"No such record found!!"},404

class BranchWiseMonthAttendance(Resource):
	def get(self,branch,month,year):
		records = mongo.db.user.find({"branch":branch},{"id":1,"_id":0})
		records = list(records)
		idlist = []
		for rec in records:
			idlist.append(rec['id'])
		total_records = []
		rgx = re.compile('.*{}-{}-.*'.format(year,month))
		for id in idlist:
			records = mongo.db.attendance.find({"id":id,"date":rgx})
			records = list(records)
			for rec in records:
				rec["_id"] = str(rec["_id"])
			total_records.extend(records)

		if total_records:
			return total_records,200
		else:
			return {"Message":"No such record found!!"},404
		
class RecentEntries(Resource):
	def get(self,name):
		records = mongo.db.user.find_one({"name":name},{"id":1,"_id":0})
		id = records['id']
		records = mongo.db.attendance.find({"id":id}).sort("date", -1).limit(7)
		records = list(records)
		for rec in records:
			rec["_id"] = str(rec["_id"])
		if records:
			return records,200
		else:
			return {"Message":"No such record found!!"},404

class UserDetails(Resource):
	def get(self):
		pass

class TodaysEntry(Resource):
	def get(self):
		date1 = str(date.today())
		records = mongo.db.attendance.find({"date":date1})
		records = list(records)
		records1 = mongo.db.user.find({},{"id":1,"name":1,"_id":0})
		records1 = list(records1)
		for rec in records:
			rec["_id"] = str(rec["_id"])
			for rec1 in records1:
				if rec['id']==rec1['id']:
					rec['name'] = rec1['name']
				
		if records:
			return records,200
		else:
			return {"Message":"No such record found!!"},404


		
		
api.add_resource(Early,'/early/<string:date1>')
api.add_resource(Late,'/late/<string:date1>')
api.add_resource(LastOne,'/lastone')
api.add_resource(AddUser,'/adduser/<int:id>/<string:name>/<branch>/<phone>/<mail>/<img>')
api.add_resource(AddAttendance,'/updateattend/<name>/<float:tim>')
api.add_resource(Forgot,'/forgot/<mail>')
api.add_resource(DailyEntry,'/dailyentry')
api.add_resource(MonthWiseAttendance,'/monthwise/<month>/<year>')
api.add_resource(UserWiseAllAttendance,'/userwise/<name>')
api.add_resource(UserWiseMonthAttendance,'/userwise/<name>/<month>/<year>')
api.add_resource(BranchWiseAllAttendance,'/branchwise/<branch>')
api.add_resource(BranchWiseMonthAttendance,'/branchwise/<branch>/<month>/<year>')
api.add_resource(RecentEntries,'/recent/<name>')
api.add_resource(TodaysEntry,'/today')
app.run(debug=True)