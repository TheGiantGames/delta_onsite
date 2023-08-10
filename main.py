import json
import random

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
app.app_context().push()
basedir = os.path.abspath(os.path.dirname(__file__))

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'Database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init marshmallow
ma = Marshmallow(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    money = db.Column(db.Integer)
    ownProperty = db.relationship('Places', backref='op')

    def __int__(self, name = name, money= money):
        self.name = name
        self.money = money

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'money': self.money,
        }


class Places(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place = db.Column(db.String)
    value = db.Column(db.Integer)
    owner = db.Column(db.Integer , db.ForeignKey('users.id'))
    #placeOwner = db.relationship('Users', backref='owner')


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'place': self.place,
            'value': self.value,
            'owner': self.owner
        }


# Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'money' , 'owner')


# init Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)


class PlaceSchema(ma.Schema):
    class Meta:
        fields = ('id', 'place', 'value')


# init Schema
place_schema = PlaceSchema()
places_schema = PlaceSchema(many=True)


buy = ""
@app.route("/buy_place/<place_id>")
def buy(place_id):
    queryPlace = db.session.query(Places).filter(Places.id == int(place_id)).first()
    queryUser = db.session.query(Users).filter(Users.money >= queryPlace.value).all()
    if len(queryUser) != 0:
        buyer=random.choice(queryUser)
        queryPlace.owner = buyer.id
        buyer.money = buyer.money - queryPlace.value
        db.session.commit()
        print(random.choice(queryUser))
        global buy
        buy = buyer.name
        return buyer.name + " is the winner of the lottery for " + queryPlace.place
    else:
        return "No Eligible buyer!!"


@app.route('/mortgage/<place_id>')
def mortgage(place_id):
    queryPlace = db.session.query(Places).filter(Places.id == int(place_id)).first()
    queryQwner  = db.session.query(Users).filter(Users.id == int(queryPlace.owner)).first()
    queryQwner.money = queryQwner.money + 0.7 * queryPlace.value
    queryPlace.value = queryPlace.value * 0.7
    db.session.commit()
    buy(place_id)
    print(queryQwner.money)
    prev_owner = str(queryQwner.name)
    new_owner = str(buy)
    exchange = queryPlace.value
    return prev_owner + " Sold his property " + queryPlace.place + " To " + new_owner + " in exchange of " + str(exchange) + " Rupees. "

@app.route('/user_ranks')
def rank():

    list1 = []
    places = db.session.query(Users).all()
    for i in range(len(places)):
        money = db.session.query(Places).filter(Places.owner == i+1).all()
        a = 0
        for j in range(len(money)):
            a = a + money[j].value
        list1.append(a)
        print(a)
    print(list1)

    list2 = []
    for i in range(len(places)):
        list2.append(places[i].money)
    print(list2)

    lst_total = []
    lst_names = []
    rank=[]
    for i in range(len(list2)):
        lst_total.append(list2[i] + list1[i])
        lst_names.append(places[i].name)
        rank.append((lst_total[i],lst_names[i]))
    return sorted(rank, reverse=True)[0:3]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
