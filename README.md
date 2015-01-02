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
- Redis
- AngularJS
- NodeJS

###### Setup

Install mongodb:
http://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/
brew install mongodb

Install Redis:
brew install redis

Clone repository
```sh
git clone git@bitbucket.org:gastonrobledo/coati.git
cd coati
pip install -r requirements.txt
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

##### Run Node Js
```sh
node app/realtime/server.js
```
