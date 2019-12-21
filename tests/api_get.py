from flask_pymongo import PyMongo


@mongomock.patch(servers=(('mongodb', 27017),))
def test_increate_votes_endpoint():
  objects = [dict(votes=1), dict(votes=2), ...]
  client = PyMongo.MongoClient('server.example.com')
  client.db.collection.insert_many(objects)
  call_endpoint('/votes')
  ... verify client.db.collection