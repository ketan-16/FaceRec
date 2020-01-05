from flask import Flask,request
from flask_restful import Resource,Api
from flask_pymongo import PyMongo
from flask_cors import CORS
import time
import smtplib
from email.message import EmailMessage
import random
from datetime import datetime,date
import csv
import re
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from security import authentication,identity
from flask_jwt import JWT,jwt_required
app =  Flask(__name__)
app.secret_key = 'FaceRec'
CORS(app)
limiter = Limiter(app,key_func=get_remote_address)
limiter.init_app(app)
app.config["MONGO_URI"]="mongodb://localhost:27017/staff"
mongo=PyMongo(app)
api = Api(app) 

jwt = JWT(app,authentication,identity)

   
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
			if start <= ten_am and rec['in']!=0.0:
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
			if start > ten_am and rec['in']!=0.0:
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
	def post(self):
		print(request.get_json())
		id = request.get_json()['id']
		name = request.get_json()['name']
		branch = request.get_json()['branch']
		phone = request.get_json()['phone']
		mail = request.get_json()['email']
		img = request.files()['img']
		mongo.db.user.insert_one({"id":id,"name":name,"branch":branch,"phone":phone,"mail":mail,"isdeleted":False,"img":None})
		return {"message":"New User added successfully!!"},201

class AddImage(Resource):
	def post(self,id):
		print(request.files)
		img = request.files()['img']
		myquery = {"id":id}
		newvalues = { "$set": { "img": img } }
		mongo.db.user.update_one(myquery, newvalues)
		return {"message":"Image added successfully!!"},201###

class LastOne(Resource):
	# @jwt_required()
	def get(self):
		records = mongo.db.user.find({},{"id":1,"_id":0}).sort("id", -1).limit(1)
		records = list(records)
		for rec in records:
			a = rec['id']
		return {"id":a},200

class AddAttendance(Resource):
	def post(self):
		name=request.get_json()['name']
		tim=request.get_json()['tim']
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
	decorators = [limiter.limit("3/day",error_message='TOO MANY REQUESTS')]
	def get(self,mail):
		records = mongo.db.OTP.find({},{"id":1,"_id":0}).sort("id", -1).limit(1)
		records = list(records)
		for rec in records:
			a = rec['id']
		value = random.randint(100000,999999)
		mongo.db.OTP.insert_one({"id":a+1,"otp":value,"mail":mail})
		msg = EmailMessage()
		msg['Subject'] = 'Forgot Password '
		msg['From'] = 'masntatu@gmail.com'
		msg['To'] = mail
		msg.add_alternative("""\
		<!DOCTYPE html>
		<html>
			<body>
				<p>Your Code is <b>{}</b> </p>
				<p>Thank you!</p>
			</body>
		</html>
		""".format(value), subtype='html')
		with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
			smtp.login('masntatu@gmail.com','mstt@12??')
			smtp.send_message(msg)
		return {"Message":"OTP sent successfully!!"},200
		

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
		
		records1 = mongo.db.user.find({},{"id":1,"name":1,"branch":1,"_id":0})
		records1 = list(records1)
		for rec in total_records:
			rec["_id"] = str(rec["_id"])
			for rec1 in records1:
				if rec['id']==rec1['id'] :
					rec['name'] = rec1['name']
					rec['branch'] = rec1['branch']
		
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


class AllUsersDetails(Resource):
	def get(self):
		records = mongo.db.user.find({},{"_id":0,"name":1,"branch":1,"phone":1,"mail":1})
		records = list(records)
		if records:
			return records,200
		else:
			return {"Message":"No such record found!!"},404
		
class UserDetails(Resource):
	def get(self,name):
		record = mongo.db.user.find_one({"name":name},{"_id":0,"name":1,"branch":1,"phone":1,"mail":1})
		if record:
			return record,200
		else:
			return {"Message":"No such record found!!"},404
		
class PeriodWiseAttendance(Resource):
	def get(self,startdate,enddate):
		# record = mongo.db.attendance.find_one({"$and":[{"id":id},{"date":dat}]})
		records = mongo.db.attendance.find({"date":{"$gte":startdate,"$lte":enddate}})
		records = list(records)
		for rec in records:
			rec["_id"] = str(rec["_id"])
		if records:
			return records,200
		else:
			return {"Message":"No such record found!!"},404

class Absent(Resource):
	def get(self,datem):
		records = mongo.db.attendance.find({"date":datem,"flag":0})
		records = list(records)
		for rec in records:
			rec["_id"] = str(rec["_id"])
		if records:
			return records,200
		else:
			return {"Message":"No such record found!!"},404

class HalfDayToday(Resource):
	def get(self):
		date1 = str(date.today())
		records = mongo.db.attendance.find({"date":date1},{"_id":0,"isforced":0,"in":0,"flag":0})
		records = list(records)
		records1 = mongo.db.user.find({},{"id":1,"name":1,"_id":0,"branch":1})
		records1 = list(records1)
		date1 = date1.split('-')
		half_day = []
		for rec in records:
			start = time.strftime("%Y %m %d %H %M %S", time.localtime(rec['out']))
			start = start.split()
			start = datetime(int(start[0]),int(start[1]),int(start[2]),int(start[3]),int(start[4]),int(start[5]))
			one_pm = datetime(int(date1[0]),int(date1[1]),int(date1[2]),15,00,00)
			if start <= one_pm and rec['out']!=0.0:
				for rec1 in records1:
					if rec['id']==rec1['id']:
						rec['name'] = rec1['name']
						rec['branch']=rec1['branch']
						half_day.append(rec)
		if half_day:
			return half_day,200
		else:
			return {"Message":"No such record found!!"},404

class EarlyDeparture(Resource):
	def get(self):
		date1 = str(date.today())
		records = mongo.db.attendance.find({"date":date1},{"_id":0,"isforced":0,"in":0,"flag":0})
		records = list(records)
		records1 = mongo.db.user.find({},{"id":1,"name":1,"_id":0,"branch":1})
		records1 = list(records1)
		date1 = date1.split('-')
		early_dep = []
		for rec in records:
			start = time.strftime("%Y %m %d %H %M %S", time.localtime(rec['out']))
			start = start.split()
			start = datetime(int(start[0]),int(start[1]),int(start[2]),int(start[3]),int(start[4]),int(start[5]))
			five_pm = datetime(int(date1[0]),int(date1[1]),int(date1[2]),15,30,00)
			if start <= five_pm and rec['out']!=0.0:
				for rec1 in records1:
					if rec['id']==rec1['id']:
						rec['name'] = rec1['name']
						rec['branch']=rec1['branch']
						early_dep.append(rec)
		if early_dep:
			return early_dep,200
		else:
			return {"Message":"No such record found!!"},404

class Authenticate(Resource):
	def post(self):
		username = request.get_json()['username']
		password = request.get_json()['password']
		record = mongo.db.Admin.find_one({"$and":[{"Email":username},{"Password":password}]})
		if record:
			return {"Message":"Logged In"}
		else:
			return {"Message":"Username and Password is wrong"}


api.add_resource(Early,'/early/<string:date1>')
api.add_resource(Late,'/late/<string:date1>')
api.add_resource(LastOne,'/lastone')
api.add_resource(AddUser,'/adduser')
api.add_resource(AddAttendance,'/updateattend')
api.add_resource(AddImage,'/addimage/<id>')
api.add_resource(Forgot,'/forgot/<mail>')
api.add_resource(DailyEntry,'/dailyentry')
api.add_resource(MonthWiseAttendance,'/monthwise/<month>/<year>')
api.add_resource(UserWiseAllAttendance,'/userwise/<name>')
api.add_resource(UserWiseMonthAttendance,'/userwise/<name>/<month>/<year>')
api.add_resource(BranchWiseAllAttendance,'/branchwise/<branch>')
api.add_resource(BranchWiseMonthAttendance,'/branchwise/<branch>/<month>/<year>')
api.add_resource(RecentEntries,'/recent/<name>')
api.add_resource(TodaysEntry,'/today')
api.add_resource(AllUsersDetails,'/usersdetails')
api.add_resource(UserDetails,'/finduser/<name>')
api.add_resource(PeriodWiseAttendance,'/periodwise/<startdate>/<enddate>')
api.add_resource(Absent,'/absent/<datem>')
api.add_resource(HalfDayToday,'/halfday')
api.add_resource(EarlyDeparture,'/earlydep')
api.add_resource(Authenticate,'/authenticate')
app.run(debug=True)

# name & dept