db.auth('test', 'test123');
db = db.getSiblingDB('testdb');
db.createUser(
        {
            user: "flask",
            pwd: "flask123",
            roles: [
                {
                    role: "readWrite",
                    db: "testdb"
                }
            ]
        }
);
