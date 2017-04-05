#!/usr/bin/env python
import requests
import os
#disable SNI warnings due to old python
requests.packages.urllib3.disable_warnings()

#baseurl
url = 'https://grafana.example.com/api'
ipaurl = 'https://ipa1.example.com/ipa/session/'
username = raw_input("Please enter admin username: ")
os.system("stty -echo")
password = raw_input("Please enter admin password: ")
os.system("stty echo")
org = raw_input("\nPlease enter orgname: ")
orguser = raw_input("Please enter orguser: ")
orguserfirstname = raw_input("Please enter orguser firstname: ")
orguserlastname = raw_input("Please enter orguser lastname: ")
orguseremail = raw_input("Please enter orguser e-mail: ")
orguserphone = raw_input("Please enter orguser phone: ")

auth = (username, password) 


orgname = {'name':org}

#login session needs x-www-form-urlencoded
ipaheaders = {'Content-Type':'application/x-www-form-urlencoded', 'Accept':'text/plain', 'referer':'https://ipa1.example.com/ipa'}
#Grafana do not care about referrer
headers = {'Accept':'application/json','Content-Type':'application/json'}
#ipa needs referrer
apiheaders = {'Content-Type': 'application/json', 'Accept':'applicaton/json', 'Referer':'https://ipa1.example.com/ipa/xml'}
#get ids of couple of admins from api/users
adminids = [8, 9, 10]
influxds = {
  'name':'Accounting',
  'type':'influxdb',
  'url':'http://influxdb.example.com:8080',
  'access':'proxy',
  'password':'radacct',
  'user':'radacct',
  'database':'radacct',
  'basicAuth':False,
  'basicAuthUser':'',
  'basicAuthPassword':'',
  'withCredentials':False,
  'isDefault':False
}

zabbixds = {
  'access':'proxy',
  'isDefault':True,
  'jsonData':{'username':'apigrapher','password':'apigrapher','trends':True},
  'name':'zabbix.example.com',
  'type':'alexanderzobnin-zabbix-datasource',
  'url':'https://zabbix.example.com/zabbix/api_jsonrpc.php'
}

ipaadd = {
    'id': 0,
    'method': 'user_add/1',
    'params': [
        [
            orguser
        ],
        {
            "gidnumber": 1538600019,
            "givenname": orguserfirstname,
            "homedirectory": "/home/lastmile",
            "loginshell": "/bin/false",
            "mail": [
               orguseremail 
            ], 
            "mobile": [
               orguserphone 
            ], 
            "noprivate": True,
            "random": True,
            "sn": orguserlastname,
            "version": "2.213"
        }
    ]
}
#login throws back session cookie
def ipaLogin():
    login = requests.post('%s/login_password' %ipaurl, headers=ipaheaders, data='user='+ username + '&password=' + password, verify=False)
    return login.cookies
#ipa generate password and return it

def addIpaUser():
    cookie = ipaLogin()
    r = requests.post('%s/json' %ipaurl, headers=apiheaders, json=ipaadd, verify=False, cookies=cookie)
    print r.text
    userpassword =  r.json()['result']['result']['randompassword']
    return userpassword

def createOrg():
    r = requests.post('%s/orgs' %url, auth=auth, data=orgname)
    return r.text

def changeOrg():
    # get numerical org id from name
    orginfo = requests.get('%s/orgs/name/%s' %(url, orgname.get('name')), auth=auth)
    # change active org to id
    r = requests.post('%s/user/using/%s' %(url, orginfo.json().get('id')), auth=auth)
    return r.text

def createDatasource():
    influx = requests.post('%s/datasources/' %url, auth=auth, headers=headers, json=influxds)
    zabbix = requests.post('%s/datasources/' %url, auth=auth,headers= headers, json=zabbixds)
    return influx.text + zabbix.text

#With LDAP basic auth first login creates user in grafana
def createUser():
    userpassword = addIpaUser()    
    createorguser = requests.get('https://grafana.example.com', auth=(orguser, userpassword))
    return createorguser.status_code

def addUsers():
    #get all users
    users = requests.get('%s/users/' %url, auth=auth)
    #format to json
    list = users.json()
    users = []
    #build list of users
    for i in range(1,len(list)):
        if 'example.com' in list[i].get('email'):
            users.append(list[i].get('email'))
        elif 'ex.com' in list[i].get('email'):
            users.append(list[i].get('email'))
    #everyone from list is added as viewer
    for user in users:
        add = requests.post('%s/org/users' %url, headers=headers,auth=auth,json={'Role':'Viewer', 'LoginOrEmail':user})
    orguseradd = requests.post('%s/org/users' %url, headers=headers,auth=auth,json={'Role':'Viewer', 'LoginOrEmail':orguser})
    return add.text + orguseradd.text

def makedashAdmins():
    for id in adminids:
        dashadmin = requests.patch('%s/org/users/%s' %(url, id), headers=headers, auth=auth, json={'Role':'Admin'})
    return dashadmin.text

#delete user from Main. Org.
#update grafana user with name/email
def changeUserOrg():
    # get numerical org id from name
    orginfo = requests.get('%s/orgs/name/%s' %(url, orgname.get('name')), auth=auth)
    # change active org to id
    orguserchange = requests.post('%s/user/using/%s' %(url, orginfo.json().get('id')), auth=(orguser, 'changeme'))
    return orguserchange.text

#print addIpaUser()
print createOrg()
print changeOrg()
print createDatasource()
print createUser()
print addUsers()
print makedashAdmins()
