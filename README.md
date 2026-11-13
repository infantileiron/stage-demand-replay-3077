# 拾光剧场 · 场次需求预演

用按时间前移的验证、递归岭回归和残差区间，把未来到场估计变成可复核的引导员编排建议，再每日生成站内透视纪要。

## 场景与边界

模拟客户是拾光剧场排演组，22人负责大剧场、黑匣子和实验厅。原先从 `attendance_daily_202611.csv` 抄取上周同日，人工估算值班人数。痛点是活动日与常规日混杂、随机切分误用未来信息，以及只有点预测没有误差说明。上游为到场记录与已知场次事件；本应用替代需求测算、复核与日报透视；下游为值班主管和入场引导组。不包含售票交易。

所有数据均为固定随机种子的模拟数据。定时报送仅在本应用内保存快照，不发送邮件、消息或外部回调。

## 页面与完整工作流

1. **排演手记**：最新预测、真实回测观测、模型/季节基线误差。
2. **历史观测**：观测档案、样本明细、结构化JSON导入与重复/容量校验。
3. **情景预演**：观测集、场馆、7/14天、周末特别场、引导员承载数。
4. **回测与解释**：队列状态、三次前移验证、最终14天回测、未来区间、生成编排建议。
5. **值班编排**：主管确认、固定纪要、带中文表头的CSV导出。
6. **报送计划**：每日北京时间计划、主管启停、下次/上次运行、历史快照下载。

共享 `DemandChart` 与 `RunStrip` 用于手记和结果页；`ForecastTable` 用于结果与编排页。图表全部读取后端计算结果。

### 角色

| 账号 | 角色 | 权限与典型动作 |
|---|---|---|
| admin@stage.local | admin | 全部分析动作；确认编排；创建/启停每日报送；查看审计 |
| analyst@stage.local | analyst | 导入观测、创建情景、提交计算、生成编排及已确认纪要；只读报送计划 |
| viewer@stage.local | viewer | 浏览结果/编排/报送；下载已确认纪要和到期快照 |

统一演示密码：`Stage2611!`。JWT有效期1小时；签名使用HS256、口令PBKDF2-SHA256（120,000轮、随机盐）。写接口在后端检查权限，隐藏按钮不作为授权控制。

### 一天的工作剧本

11:00 林予以分析员身份核对 `attendance_daily_202611.csv` 的1,260条观测；11:05 选择大剧场420天历史；11:08 新建“11月第二周常规场”，预测7天、每65名观众配1名引导员；11:10 提交Redis队列；11:11 比较岭回归与上周同日MAE、阅读区间；11:15 生成“11月第二周引导员建议”；11:20 陈溪以主管身份确认；11:25 分析员生成纪要并下载；主管设定每日08:30报送；次日由worker固化日期×厅透视快照，值班组下载。

## 快速启动

需要Docker Compose v2和可用镜像/依赖网络：

```sh
cp .env.example .env
docker compose config --quiet
docker compose up -d --build
# 自动seed；以下命令可安全重复执行
docker compose exec -T backend python -m scripts.seed_demo
docker compose ps
```

访问 [前端](http://localhost:18203)、[后端文档](http://localhost:19203/docs)。MySQL宿主端口17703；Redis和worker不暴露宿主端口。收尾运行 `docker compose down -v --remove-orphans`，此命令会清除本项目命名卷。

### 技术与部署

| 部分 | 实现 |
|---|---|
| frontend | Vue3.5、TypeScript5.7、Vite6、Nginx1.27 |
| backend | Python3.11、FastAPI、NumPy；参数化SQL，PyMySQL8连接 |
| worker | Python独立进程，Redis RESP队列消费及站内到期报送 |
| db | MySQL8.0；6类核心实体，JSON文档载荷及唯一自然键 |
| redis | Redis7，AOF命名卷 |

Compose恰好五服务，均带healthcheck。后端依赖db/redis健康，前端依赖后端健康；worker依赖后端/db/redis。命名卷包括数据库、Redis和后端/worker共享产物。Nginx将 `/api/` 去前缀代理到后端；后端路由本身不含 `/api`。worker心跳检查同时验证Redis可用。当前只部署一个worker；Redis列表取出任务后若进程崩溃，不保证自动重放，需查看未完成任务并重新提交。

## 数据与算法口径

seed使用随机种子 `261104`：2025-09-17至2026-11-10共420天，三个厅共1,260行；大剧场容量800、黑匣子300、实验厅500。含三个角色、两个情景、一份实际计算结果、已确认编排、纪要和每日08:30站内报送计划。自然键存在时只读取，既不增加重复行，也不覆盖人工修改。

### 算法1：递归岭回归与时间验证

按所选厅、日期升序，使用 lag1、lag7、过去7天均值、周末、已知特别场和日期趋势。标准化均值/方差只在各训练窗计算。最小化

`||y - Xβ||² + α||β_except_intercept||²`

以扩展训练窗的三段14天递归MAE选择 `α ∈ {0.1,1,10,100}`；最后14天完全不参与参数选择。递归预测使用自己的上一步预测，不读取未来真实到场。最终与“上周同日”递归朴素模型比较。最终预测重训全部历史、外推7/14天并截断至容量。最短70天；日期缺口、重复、容量变化和超容量人数均拒绝计算。

### 算法2：残差分位区间与人力建议

以保留14天递归预测的绝对残差排序，取 `ceil((n+1)×0.9)` 位（上限n）作为半径；预测上下界截断至 `[0,容量]`。引导员建议为 `max(2, ceil(上界/每名承载人数))`。这是近期残差区间，遇到漂移、相关残差和多步远期不保证90%覆盖；并非因果或销售承诺。

### 透视与定时报送

- 行：预演日期；列：场馆×（预测人数、预测上座率、引导员建议）。
- 预测人数是日到场点预测；预测上座率=`预测人数/容量×100%`，不是实收票占比；引导员按区间上界计算。
- 默认从每个厅最近一份已确认纪要取数，避免同一计划版本重复汇总；也可锁定一份纪要。
- 每日时刻使用UTC+08:00。worker先处理到期计划，再等待队列，正常轮询约2秒。快照自然键为 `schedule_id:业务日期`，重试不会覆盖已生成内容。
- 暂停后不报送。启用后安排下个时刻。停机后补一次最早逾期日，再进入当前时间之后的下个时刻，不追补所有历史日报。

### 导入格式

历史页接受最多5,000行、1.5MB的JSON数组，避免CSV的日期/地区格式歧义。模拟CSV文件名作为上游来源标识。

```json
[{"date":"2026-11-01","venue":"大剧场","attendance":480,"capacity":800,"event":0}]
```

每份文件至少42行，运行某厅预测需该厅至少70天连续历史。

## 核心实体与目录

`AttendanceDataset → ForecastScenario → ForecastRun → StaffingPlan → Report → DeliverySchedule`。

每类实体分别有 `backend/src/{models,schemas,services,controllers,routes}/<实体>.py` 与前端 `src/{api,stores}/<实体>.ts`；数据库实体为datasets/scenarios/runs/plans/reports/schedules。delivery_snapshots是报送技术产物表，users/audit为横切表。文档载荷由dataclass模型持久化，身份/时间由参数化repository处理；结构SQL在 `backend/migrations/001_initial.sql`。

```text
backend/src/           路由、控制器、服务、模型、校验、中间件、配置
backend/scripts/       幂等seed
backend/migrations/    MySQL初始结构
frontend/src/          API、状态、六业务页、组件、hooks与工具
docker-compose.yml    五服务独立栈
```

### 共享枚举位置

| 枚举 | 后端定义/使用 | 前端定义/使用 |
|---|---|---|
| Role | constants/enums.py；utils/dependencies.py | constants/enums.ts；stores/auth.ts、App.ts |
| RunStatus | constants/enums.py；services/run.py、services/plan.py | constants/enums.ts、types/domain.ts；RunStrip、Results |
| ReviewStatus | constants/enums.py；services/plan.py | constants/enums.ts、types/domain.ts；Plans |

审计与全局错误处理分别位于 `middlewares/audit.py`、`middlewares/errors.py`。队列同时活动任务上限10，过载429；队列不可用明确503并保留失败记录。

### 环境变量

| 变量 | 默认/含义 |
|---|---|
| COMPOSE_PROJECT_NAME | stage-demand |
| FRONTEND_PORT / BACKEND_PORT / DB_PORT | 18203 / 19203 / 17703 |
| DB_PASSWORD / DB_ROOT_PASSWORD | 演示密码，部署时修改 |
| JWT_SECRET | 演示签名密钥，部署时修改 |
| SEED_DEMO | true，启动自动执行插入式seed，失败记录日志 |
| DATABASE_URL | Compose注入MySQL URL；本地可显式使用sqlite:///绝对路径 |
| REDIS_HOST / REDIS_PORT | redis / 6379 |
| ARTIFACTS_DIR | /app/artifacts，共享卷保留作产物扩展 |

## 本地开发与验证

```sh
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
DATABASE_URL=sqlite:////tmp/stage-dev.sqlite3 SEED_DEMO=true .venv/bin/uvicorn src.main:app --port 19203
# 另一个终端；后台执行仍需要实际Redis
DATABASE_URL=sqlite:////tmp/stage-dev.sqlite3 REDIS_HOST=127.0.0.1 .venv/bin/python -m src.worker
# 前端（从backend目录返回）
cd ../frontend
npm install
npm run dev -- --port 18203
```

本地Vite将 `/api` 代理到19203。`/health` 同时验证数据库和Redis，不会把缺少Redis的本地开发会话标健康。

测试脚本与记录位于批次目录 `test-artifacts/gb-2104/`。`tests/test_local.py` 是SQLite与TestClient验证，直接调用真实worker处理函数、只替换入队传输；不代表Redis/MySQL或容器验收。`tests/docker_acceptance.py` 只对真实栈运行，真实轮询后台计算及下一分钟定时报送，不包含inline替代，默认 `BASE_URL=http://127.0.0.1:19203`。

当前状态是 **partial**：本地18项测试和Compose配置已通过；Docker socket访问、Vue依赖下载和headless浏览器环境受限，五服务健康、MySQL/Redis集成、前端构建和四张截图尚未完成。详见独立 `TESTING.md`，不能将本地验证等同于容器通过。

## License

MIT，见LICENSE。
