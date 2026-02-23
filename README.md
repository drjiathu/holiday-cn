# holiday-cn

中国法定节假日数据，每日自动抓取国务院公告。

- [x] 提供 JSON 格式节假日数据
- [x] 提供 REST API 查询服务
- [x] 支持 Docker 部署
- [x] CI 自动更新
- [x] 数据变化时自动发布新版本 ( `Watch` - `Release only` 以获取邮件提醒! )
- [x] [发布页面]提供 JSON 打包下载

数据格式:

[JSON Schema](./schema.json)

``` TypeScript
interface Holidays {
  /** 完整年份, 整数。*/
  year: number;
  /** 所用国务院文件网址列表 */
  papers: string[];
  days: {
    /** 节日名称 */
    name: string;
    /** 日期, ISO 8601 格式 */
    date: string;
    /** 是否为休息日 */
    isOffDay: boolean;
  }[]
}
```

## 注意事项

- **年份是按照国务院文件标题年份而不是日期年份**，12 月份的日期可能会被下一年的文件影响，因此应检查两个文件。
- 与周末连休的周末不是法定节假日，数据里不会包含，参见[《全国年节及纪念日放假办法》](https://www.gov.cn/gongbao/content/2014/content_2561284.htm)。

## CDN 访问

通过 jsDelivr CDN 免费访问数据，无需自建服务：

| 类型 | 地址 |
|------|------|
| JSON 数据 | `https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/{year}.json` |
| 年度日历 | `https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/{year}.ics` |
| 合集日历 | `https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/holiday-cn.ics` |

- `{year}.ics` 为对应年份的节假日
- `holiday-cn.ics` 为近 5 年的节假日合集，可直接导入日历应用

示例代码参见 [examples/](./examples/) 目录。

## API 服务

提供 REST API 查询节假日数据。

### API 端点

| 端点 | 说明 | 示例 |
|------|------|------|
| `GET /` | API 信息 | - |
| `GET /date/{date}` | 查询指定日期 | `/date/2024-10-01` |
| `GET /today` | 查询今天 | - |
| `GET /year/{year}` | 获取年度数据 | `/year/2024` |
| `GET /range?start={start}&end={end}` | 查询日期范围 | `/range?start=2024-01-01&end=2024-12-31` |

### 响应示例

**查询指定日期** `GET /date/2024-10-01`

```json
{
  "date": "2024-10-01",
  "isHoliday": true,
  "isOffDay": true,
  "name": "国庆节"
}
```

**查询日期范围** `GET /range?start=2024-10-01&end=2024-10-07`

```json
{
  "start": "2024-10-01",
  "end": "2024-10-07",
  "days": [
    {"date": "2024-10-01", "name": "国庆节", "isOffDay": true},
    {"date": "2024-10-02", "name": "国庆节", "isOffDay": true},
    {"date": "2024-10-03", "name": "国庆节", "isOffDay": true}
  ]
}
```

### 本地运行

```bash
# 安装依赖
poetry install

# 启动服务
uvicorn holiday_cn.api:app --host 0.0.0.0 --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

## Docker 部署

支持一键部署，同时提供 API 服务和定时数据更新。

### 一键部署

```bash
# 启动服务（首次会自动获取数据）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

首次启动时，容器会自动检测并获取当前年份的节假日数据，之后按计划定时更新。

### 手动操作

```bash
# 手动触发数据更新
docker exec holiday-cn python -m holiday_cn.entry

# 查看定时任务日志
docker exec holiday-cn cat /var/log/cron.log

# 查看容器状态
docker-compose ps
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `CRON_SCHEDULE` | 定时更新的 cron 表达式 | `0 12 * * *` |

**常用 cron 表达式：**

| 表达式 | 说明 |
|--------|------|
| `0 12 * * *` | 每天中午 12:00 |
| `0 */6 * * *` | 每 6 小时 |
| `0 8,20 * * *` | 每天 8:00 和 20:00 |
| `0 0 * * 1` | 每周一凌晨 |

### 自定义配置

修改 `docker-compose.yml` 中的环境变量：

```yaml
environment:
  - CRON_SCHEDULE=0 8,20 * * *  # 每天 8:00 和 20:00 更新
```

### 注意事项

- 数据存储在 `./data` 目录，通过 volume 挂载到容器
- 容器重启后会保留数据，无需重新获取
- 健康检查每 30 秒执行一次，确保服务可用

[发布页面]: https://github.com/drjiathu/holiday-cn/releases
