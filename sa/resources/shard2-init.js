rs.initiate(
  {
     _id: "iabdshard2",
     version: 1,
     members: [
        { _id: 0, host : "mongo-shard2a:27017" },
        { _id: 1, host : "mongo-shard2b:27017" },
     ]
  }
)