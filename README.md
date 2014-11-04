# Coati 1.0
----
#### Agile project management
----
###### Technologies

- Flask
    - MongoEngine
    - Flask-RestFul
    - OAuth
- MongoDB
- AngularJS
- NodeJS

###### Setup

Install mongodb:
http://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/

Clone repository
```sh
git clone git@bitbucket.org:gastonrobledo/coati.git
```

Compile FrontEnd
```sh
cd coati/frontend
npm install
bower install
grunt build
```

###### Run application
```sh
python coati/run.py
```