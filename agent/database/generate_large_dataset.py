import os
import random
import datetime

# ==============================================================================
# 1. 模拟参数定义 (基于阿里云真实参数与定价体系)
# ==============================================================================
PRODUCTS = {
    # ECS 计算与通用型实例 (单月包年包月单价)
    "ecs.g8a.xlarge": {"name": "第八代通用型 ecs.g8a.xlarge (4核16G)", "base_price": 299.00, "category": "ECS"},
    "ecs.g8a.4xlarge": {"name": "第八代通用型 ecs.g8a.4xlarge (16核64G)", "base_price": 1250.00, "category": "ECS"},
    "ecs.g8a.8xlarge": {"name": "第八代通用型 ecs.g8a.8xlarge (32核128G)", "base_price": 2400.00, "category": "ECS"},
    "ecs.c7.large": {"name": "第七代计算型 ecs.c7.large (2核4G)", "base_price": 120.00, "category": "ECS"},
    "ecs.c7.8xlarge": {"name": "第七代计算型 ecs.c7.8xlarge (32核64G)", "base_price": 1299.00, "category": "ECS"},
    "ecs.gn7i-c8g1.2xlarge": {"name": "GPU 计算型 ecs.gn7i-c8g1.2xlarge (8核32G, 1*A10)", "base_price": 3500.00, "category": "GPU"},
    
    # RDS 关系型数据库 (单月单价)
    "rds.mysql.c1.large": {"name": "云数据库 RDS MySQL 高可用版 (2核4G)", "base_price": 599.00, "category": "RDS"},
    "rds.mysql.c2.xlarge": {"name": "云数据库 RDS MySQL 高可用版 (4核8G)", "base_price": 1099.00, "category": "RDS"},
    
    # 存储与带宽
    "essd.pl1.100g": {"name": "ESSD PL1 性能云盘 (100G)", "base_price": 50.00, "category": "DISK"},
    "bandwidth.100m": {"name": "共享带宽 (100Mbps)", "base_price": 150.00, "category": "BANDWIDTH"}
}

REGIONS = [
    ("cn-beijing", ["cn-beijing-h", "cn-beijing-k", "cn-beijing-l"]),
    ("cn-hangzhou", ["cn-hangzhou-g", "cn-hangzhou-h", "cn-hangzhou-i"]),
    ("cn-shanghai", ["cn-shanghai-f", "cn-shanghai-g", "cn-shanghai-n"]),
    ("cn-shenzhen", ["cn-shenzhen-e", "cn-shenzhen-f"])
]

USER_COUNT = 50       # 生成 50 个真实用户
DAYS_OF_METRICS = 30  # 每个实例生成 30 天的历史监控数据以供图表和趋势诊断

# ==============================================================================
# 2. 生成模拟数据集的 Python 逻辑
# ==============================================================================
def generate_dataset():
    orders = []
    instances = []
    metrics = []
    
    # 设定日期基准 (今天)
    today = datetime.date.today()
    
    # 用户身份画像分类，以产生多样化的业务数据
    # user_1001 至 user_1050
    for u_idx in range(1, USER_COUNT + 1):
        user_id = f"user_{1000 + u_idx}"
        
        # 1. 确定该用户的业务特性与画像分类
        # 20% 的大客户 (资源闲置闲钱多，极好触发 FinOps)
        # 20% 的紧凑高负荷客户 (机器快爆了，适合做升级推荐)
        # 50% 的普通健康客户 (日常波动)
        # 10% 的流失/停机客户 (服务器已关机)
        rand_val = random.random()
        if rand_val < 0.20:
            persona = "IDLE_GIANT"
        elif rand_val < 0.40:
            persona = "TIGHT_STARTUP"
        elif rand_val < 0.90:
            persona = "NORMAL_HEALTHY"
        else:
            persona = "STOPPED_USER"
            
        # 2. 为用户生成订单 (2 - 6 笔)
        order_count = random.randint(2, 6)
        user_paid_order_ids = []
        
        for o_idx in range(1, order_count + 1):
            order_id = f"ORD-{1000 + u_idx}-{o_idx:03d}"
            
            # 根据画像推荐购买的产品
            if persona == "IDLE_GIANT":
                # 大客户喜欢买昂贵的高配产品
                prod_key = random.choice(["ecs.g8a.8xlarge", "ecs.g8a.4xlarge", "ecs.gn7i-c8g1.2xlarge", "rds.mysql.c2.xlarge"])
            elif persona == "TIGHT_STARTUP":
                # 创业公司喜欢省钱买低规格但跑很重的任务
                prod_key = random.choice(["ecs.c7.large", "rds.mysql.c1.large"])
            else:
                # 普通用户按概率选择
                prod_key = random.choice(list(PRODUCTS.keys()))
                
            prod_info = PRODUCTS[prod_key]
            billing_mode = "包年包月" if random.random() > 0.3 else "按量付费"
            
            # 计算价格
            if billing_mode == "包年包月":
                months = random.choice([1, 3, 6, 12])
                amount = prod_info["base_price"] * months
            else:
                # 按量付费的订单一般是单日结算账单金额
                amount = round(prod_info["base_price"] / 30.0 * random.uniform(0.8, 1.5), 2)
                
            status = "Paid" if random.random() > 0.05 else "Unpaid" # 5% 概率存在未支付账单
            created_days_ago = random.randint(10, 180)
            created_time = today - datetime.timedelta(days=created_days_ago)
            created_str = created_time.strftime("%Y-%m-%d %H:%M:%S")
            
            orders.append({
                "order_id": order_id,
                "user_id": user_id,
                "product_name": prod_info["name"],
                "billing_mode": billing_mode,
                "amount": amount,
                "status": status,
                "created_at": created_str
            })
            
            if status == "Paid" and prod_info["category"] in ["ECS", "GPU", "RDS"]:
                user_paid_order_ids.append((order_id, prod_key))
                
        # 3. 为已支付的核心产品生成对应的资源实例 (1 - 3 台)
        inst_count = min(len(user_paid_order_ids), random.randint(1, 3))
        selected_orders = random.sample(user_paid_order_ids, inst_count) if user_paid_order_ids else []
        
        for idx, (order_id, prod_key) in enumerate(selected_orders):
            inst_prefix = "rm-" if PRODUCTS[prod_key]["category"] == "RDS" else "i-"
            instance_id = f"{inst_prefix}bp1-{user_id[-4:]}-{idx+1}"
            
            region_name, zones = random.choice(REGIONS)
            zone_name = random.choice(zones)
            
            # 运行状态由画像决定
            if persona == "STOPPED_USER":
                status = "Stopped"
                public_ip = "NULL"
            else:
                status = "Running" if random.random() > 0.1 else "Stopped"
                public_ip = f"'{random.randint(47, 123)}.{random.randint(10, 200)}.{random.randint(1, 254)}.{random.randint(1, 254)}'" if status == "Running" and inst_prefix == "i-" else "NULL"
                
            instances.append({
                "instance_id": instance_id,
                "user_id": user_id,
                "order_id": order_id,
                "instance_type": prod_key,
                "region_id": region_name,
                "zone_id": zone_name,
                "status": status,
                "public_ip": public_ip
            })
            
            # 4. 生成该实例近 30 天的历史监控数据 (每日一条)
            if status == "Running":
                for day_offset in range(DAYS_OF_METRICS):
                    metric_date = today - datetime.timedelta(days=(DAYS_OF_METRICS - day_offset - 1))
                    
                    # 根据用户画像，模拟极具代表性的性能正态分布曲线
                    if persona == "IDLE_GIANT":
                        # 资源闲置：CPU < 5%，内存 < 20%
                        cpu = round(random.normalvariate(2.2, 0.8), 2)
                        cpu = max(0.5, min(6.0, cpu))  # 边界约束
                        mem = round(random.normalvariate(14.5, 2.0), 2)
                        mem = max(5.0, min(25.0, mem))
                        bw = round(random.normalvariate(0.8, 0.3), 2)
                        bw = max(0.1, min(3.0, bw))
                    elif persona == "TIGHT_STARTUP":
                        # 高负荷：CPU > 80%，内存 > 85%
                        cpu = round(random.normalvariate(84.0, 4.5), 2)
                        cpu = max(70.0, min(99.8, cpu))
                        mem = round(random.normalvariate(89.0, 3.0), 2)
                        mem = max(80.0, min(98.5, mem))
                        bw = round(random.normalvariate(65.0, 12.0), 2)
                        bw = max(20.0, min(99.0, bw))
                    else:
                        # 普通健康机器：CPU 15%~45%，内存 30%~60%
                        cpu = round(random.normalvariate(32.0, 8.0), 2)
                        cpu = max(5.0, min(65.0, cpu))
                        mem = round(random.normalvariate(44.0, 6.0), 2)
                        mem = max(20.0, min(75.0, mem))
                        bw = round(random.normalvariate(12.5, 4.0), 2)
                        bw = max(1.0, min(35.0, bw))
                        
                    metrics.append({
                        "instance_id": instance_id,
                        "user_id": user_id,
                        "metric_date": metric_date.strftime("%Y-%m-%d"),
                        "avg_cpu_usage_percent": cpu,
                        "avg_memory_usage_percent": mem,
                        "max_network_out_mbps": bw
                    })
                    
    return orders, instances, metrics

# ==============================================================================
# 3. 将生成的数据集输出为高雅的 SQL 文件
# ==============================================================================
def write_sql_file(orders, instances, metrics):
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init_large_mock_data.sql")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("""-- ==============================================================================
-- 云平台大规模用户订单、资产实例与性能监控高仿真数据集 (生产级规模测试)
-- 包含 50 个真实画像用户，百余个资源实例，以及过去 30 天的系统级监控指标
-- ==============================================================================

-- 1. 创建订单表 (如果不存在)
CREATE TABLE IF NOT EXISTS cloud_orders (
    order_id VARCHAR(50) PRIMARY KEY COMMENT '订单唯一ID',
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
    billing_mode VARCHAR(20) NOT NULL COMMENT '计费模式 (包年包月, 按量付费)',
    amount DECIMAL(10, 2) NOT NULL COMMENT '订单金额',
    status VARCHAR(20) NOT NULL COMMENT '订单状态 (Paid, Unpaid, Refunded)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='云产品订单表';

-- 2. 创建资源实例表 (如果不存在)
CREATE TABLE IF NOT EXISTS cloud_instances (
    instance_id VARCHAR(50) PRIMARY KEY COMMENT '资源实例ID',
    user_id VARCHAR(50) NOT NULL COMMENT '所属用户',
    order_id VARCHAR(50) NOT NULL COMMENT '关联的购买订单',
    instance_type VARCHAR(100) NOT NULL COMMENT '实例规格',
    region_id VARCHAR(50) NOT NULL COMMENT '所在地域',
    zone_id VARCHAR(50) NOT NULL COMMENT '所在可用区',
    status VARCHAR(20) NOT NULL COMMENT '实例运行状态 (Running, Stopped)',
    public_ip VARCHAR(20) COMMENT '公网 IP',
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='云资源实例表';

-- 3. 创建日级监控指标表 (如果不存在)
CREATE TABLE IF NOT EXISTS instance_metrics_daily (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
    instance_id VARCHAR(50) NOT NULL COMMENT '实例ID',
    user_id VARCHAR(50) NOT NULL COMMENT '所属用户ID',
    metric_date DATE NOT NULL COMMENT '统计日期',
    avg_cpu_usage_percent DECIMAL(5,2) NOT NULL COMMENT '当日平均CPU利用率',
    avg_memory_usage_percent DECIMAL(5,2) NOT NULL COMMENT '当日平均内存利用率',
    max_network_out_mbps DECIMAL(8,2) NOT NULL COMMENT '当日出口带宽峰值(Mbps)',
    INDEX idx_instance_date (instance_id, metric_date),
    INDEX idx_user_instance (user_id, instance_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实例日级监控指标表';

-- ------------------------------------------------------------------------------
-- 清空旧有测试数据以进行重置
-- ------------------------------------------------------------------------------
TRUNCATE TABLE cloud_orders;
TRUNCATE TABLE cloud_instances;
TRUNCATE TABLE instance_metrics_daily;

""")

        # ----------------------------------------------------------------------
        # 写入订单数据
        # ----------------------------------------------------------------------
        f.write("\n-- ------------------------------------------------------------------------------\n")
        f.write("-- 插入订单数据集 (约 200 笔订单)\n")
        f.write("-- ------------------------------------------------------------------------------\n")
        f.write("INSERT INTO cloud_orders (order_id, user_id, product_name, billing_mode, amount, status, created_at) VALUES\n")
        
        order_values = []
        for o in orders:
            order_values.append(f"('{o['order_id']}', '{o['user_id']}', '{o['product_name']}', '{o['billing_mode']}', {o['amount']}, '{o['status']}', '{o['created_at']}')")
            
        f.write(",\n".join(order_values) + ";\n")

        # ----------------------------------------------------------------------
        # 写入实例数据
        # ----------------------------------------------------------------------
        f.write("\n-- ------------------------------------------------------------------------------\n")
        f.write("-- 插入实例资源数据集 (包含 ECS、GPU 算力、RDS 数据库等)\n")
        f.write("-- ------------------------------------------------------------------------------\n")
        f.write("INSERT INTO cloud_instances (instance_id, user_id, order_id, instance_type, region_id, zone_id, status, public_ip) VALUES\n")
        
        inst_values = []
        for i in instances:
            inst_values.append(f"('{i['instance_id']}', '{i['user_id']}', '{i['order_id']}', '{i['instance_type']}', '{i['region_id']}', '{i['zone_id']}', '{i['status']}', {i['public_ip']})")
            
        f.write(",\n".join(inst_values) + ";\n")

        # ----------------------------------------------------------------------
        # 写入监控数据 (使用大批量分批插入以防止 SQL 执行解析器过载)
        # ----------------------------------------------------------------------
        f.write("\n-- ------------------------------------------------------------------------------\n")
        f.write(f"-- 插入监控历史数据集 (包含 {len(metrics)} 条 CPU/RAM/带宽 日度遥测记录)\n")
        f.write("-- ------------------------------------------------------------------------------\n")
        
        # 每 500 行做一次 INSERT 语句以支持高可靠性执行
        batch_size = 500
        for b_start in range(0, len(metrics), batch_size):
            batch = metrics[b_start : b_start + batch_size]
            f.write("INSERT INTO instance_metrics_daily (instance_id, user_id, metric_date, avg_cpu_usage_percent, avg_memory_usage_percent, max_network_out_mbps) VALUES\n")
            
            metric_values = []
            for m in batch:
                metric_values.append(f"('{m['instance_id']}', '{m['user_id']}', '{m['metric_date']}', {m['avg_cpu_usage_percent']}, {m['avg_memory_usage_percent']}, {m['max_network_out_mbps']})")
                
            f.write(",\n".join(metric_values) + ";\n\n")
            
    print(f"[OK] Successfully generated large-scale simulated SQL dataset: {output_path}")
    print(f"   - Order records: {len(orders)} rows")
    print(f"   - Resource instances: {len(instances)} units")
    print(f"   - Metrics logs: {len(metrics)} rows (30-day historical telemetry)")

if __name__ == "__main__":
    orders, instances, metrics = generate_dataset()
    write_sql_file(orders, instances, metrics)
