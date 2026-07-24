// 宠迹 MongoDB 初始化脚本
// 创建 TTL 索引（免费用户7天自动清理）

db = db.getSiblingDB('pawtrack');

// 1. 定位轨迹集合
db.createCollection('locations');
db.locations.createIndex({ "device_id": 1, "created_at": -1 });
db.locations.createIndex({ "pet_id": 1, "created_at": -1 });
// 免费用户 TTL（7天 = 604800秒）
db.locations.createIndex({ "created_at": 1 }, { expireAfterSeconds: 604800 });

// 2. 设备状态集合
db.createCollection('device_status');
db.device_status.createIndex({ "device_id": 1 }, { unique: true });
db.device_status.createIndex({ "updated_at": 1 }, { expireAfterSeconds: 86400 });

print("✅ MongoDB 初始化完成");
