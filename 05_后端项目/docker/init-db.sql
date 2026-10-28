-- 宠迹 PawTrack 数据库扩展初始化
-- 业务表结构由后端应用启动时的单进程 create_all 统一创建，避免双份 DDL 漂移。

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

SELECT '✅ 宠迹数据库扩展初始化完成' AS result;
