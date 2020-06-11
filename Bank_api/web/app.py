#import the library
from flask import Flask,jsonify,request
from flask_restful import Api,Resource
from pymongo import MongoClient
import bcrypt

#constructing the api
app =Flask(__name__)
api=Api(app)

#creating the database
client=MongoClient("mongobd//db:27017")
db=client.BankApi
users=db["users"]

#helper function 
def UserExist(username):
    if users.find({"Username":username}).count==0:
        return False
    else:
        return True

class Register(Resource):
    def post(self):
        postedData=request.get_json()
        
        username= postedData["username"]
        password= postedData["password"]
        
        if UserExist(username):
            return jsonify(genrateRetunDictinory(301,'invalid user'))
        
        hashed_pw=bcrypt.hashpw(password.encode("utf8"),bcrypt.gensalt())
        
        users.insert({
            "Username":username,
            "Password":hashed_pw,
            "Own":0,
            "Debt":0
            })
        
        return jsonify(genrateRetunDictinory(301, "You are succesfully singned up for api"))

def verifyPw(username,password):
    if not UserExist(username):
        return False
    
    hashed_pw=users.find({
        "Username":username
        })[0]["Password"]
    
    if bcrypt.hashedpw(password.encode("utf8"), hashed_pw)==hashed_pw:
        return True
    else:
        return False
    
def cashWithUser(username):
    cash=users.find({
        "Username":username})[0]["Own"]
    return cash

def debtWithUser(username):
    debt=users.find({
        "Username":username})[0]["debt"]
    return debt

def genrateRetunDictinory(status,msg):
    retjson={
        "status":status,
        "msg":msg
        }
    return retjson

def verifyCredential(username,password):
    if not UserExist(username):
        return genrateRetunDictinory(301, "Invalid password"),True
    
    correct_pw=verifyPw(username, password)
    
    if not correct_pw:
        return genrateRetunDictinory(302, "Incorrect password"),True
    
    return None,False

def updateAccount(username,balance):
    users.update({
        },{
            "$set":{
                "Own":balance
                }
            })
            
def updateDebt(username,balance):
    users.update({
        },{
            "$set":{
                "debt":balance}
            })

class Add(Resource):
    def post(self):
        postedData=request.get_json()
        
        username=postedData["username"]
        password=postedData["password"]
        money=postedData["amount"]
        
        retjson,error=verifyCredential(username, password)
        
        if error:
            return jsonify(retjson)
        
        if money<=0:
            return jsonify(genrateRetunDictinory(304, "Not enought money"))
        
        cash=cashWithUser(username)
        
        money-=1
        
        bank_cash =cashWithUser("BANK")
        updateAccount("BANK", bank_cash+1)
        updateAccount(username, cash+money)
        
        return jsonify(genrateRetunDictinory(200, "Amount add sucefully  to account"))
    
class Transfer(Resource):
    def post(self):
        postedData=request.get_json()
        
        username=postedData["username"]
        password=postedData["password"]
        to=postedData["to"]
        money=postedData["amount"]
        
        retjson,error=verifyCredential(username, password)
        
        if error:
            return jsonify(retjson)
        
        cash=cashWithUser(username)
        
        if cash<=money:
            return jsonify(genrateRetunDictinory(304, "you are out of money"))
        
        if not UserExist(to):
            return jsonify(genrateRetunDictinory(301, "Recevir user not exist"))
        
        cash_from=cashWithUser(username)
        cash_to=cashWithUser(to)
        bank_cash=cashWithUser("BANK")
        
        updateAccount("BANK", bank_cash+1)
        updateAccount(to, cash_to+money-1)
        updateAccount(username, cash_from-money)
        
        return jsonify(genrateRetunDictinory(200, " Amount Transfer"))


class Blance(Resource):
    def post(self):
        postedData=request.get_json()
        
        username=postedData["username"]
        password=postedData["password"]
        
        retjson,error=verifyCredential(username, password)
        
        if error:
            return jsonify(retjson)
        
        retjson=users.find({
            "Username":username
            },{
                "Password":0,
                "_id":0
            })[0]
        return jsonify(retjson)
    
class Takeloan(Resource):
    def post(self):
        postedData=request.get_json()
        
        username=postedData["username"]
        password=postedData["password"]
        loan=postedData["amount"]
        
        retjson,error=verifyCredential(username, password)
        
        if error:
            return jsonify(retjson)        
        
        cash =cashWithUser(username)
        debt=debtWithUser(username)
        
        updateAccount(username, cash+loan)
        updateDebt(username,debt+loan)
        
        return jsonify(genrateRetunDictinory(200, "Loan is tranfer"))
    
class Payloan(Resource):
    def post(self):
        postedData=request.get_json()
        
        username=postedData["username"]
        password=postedData["password"]
        pay=postedData["amount"]
        
        retjson,error=verifyCredential(username, password)
        
        if error:
            return jsonify(retjson)   
        
        
        cash =cashWithUser(username)
        if cash<=pay:
            return jsonify(genrateRetunDictinory(301, "Not enought cash to pay"))
        
        
        debt=debtWithUser(username)
        
        updateAccount(username, cash-pay)
        updateDebt(username,debt-pay)
        
        return jsonify(genrateRetunDictinory(200, "Loan is pay"))
    
api.add_resource(Payloan, "/payloan")
api.add_resource(Takeloan, "/takeloan")
api.add_resource(Blance,"/blance")
api.add_resource(Transfer,"/transfer")
api.add_resource(Add,"/add")
api.add_resource(Register,"/register")        

if __name__=="__main__":
    app.run(host='0.0.0.0')
            
    