import requests
import os
#disable SNI warnings due to old python
requests.packages.urllib3.disable_warnings()

#baseurl
url = 'https://change.me/api'

username = raw_input("Please enter username: ")
os.system("stty -echo")
password = raw_input("Please enter password: ")
os.system("stty echo")
org = raw_input("\nPlease enter orgname: ")
orguser = raw_input("Please enter orguser: ")

auth = (username, password) 

orgname = {'name':org}
headers = {'Accept':'application/json','Content-Type':'application/json'}
#get ids of couple of admins from api/users
adminids = [8, 9, 10]
influxds = {
  'name':'Datasource1',
  'type':'influxdb',
  'url':'http://change.me:8080',
  'access':'proxy',
  'password':'',
  'user':'',
  'database':'',
  'basicAuth':False,
  'basicAuthUser':'',
  'basicAuthPassword':'',
  'withCredentials':False,
  'isDefault':False
}

zabbixds = {
  'access':'proxy',
  'isDefault':True,
  'jsonData':{'username':'zabbixuser','password':'zabbixpwd','trends':True},
  'name':'change.me',
  'type':'alexanderzobnin-zabbix-datasource',
  'url':'https://change.me/zabbix/api_jsonrpc.php'
}

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

def addUsers():
    #get all users
    users = requests.get('%s/users/' %url, auth=auth)
    #format to json
    list = users.json()
    yourusers = []
    #build list of users from e-mail domain
    for i in range(1,len(list)):
        if 'change.me' in list[i].get('email'):
            yourusers.append(list[i].get('email'))
    #everyone from list is added as viewer
    for user in yourusers:
        add = requests.post('%s/org/users' %url, headers=headers,auth=auth,json={'Role':'Viewer', 'LoginOrEmail':user})
    orguseradd = requests.post('%s/org/users' %url, headers=headers,auth=auth,json={'Role':'Viewer', 'LoginOrEmail':orguser})
    return add.text + orguseradd.text

def makedashAdmins():
    for id in adminids:
        dashadmin = requests.patch('%s/org/users/%s' %(url, id), headers=headers, auth=auth, json={'Role':'Admin'})
    return dashadmin.text

print createOrg()
print changeOrg()
print createDatasource()
print addUsers()
print makedashAdmins()
