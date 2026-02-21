# holiday-cn

中国法定节假日数据，每日自动抓取国务院公告。

- [x] 提供 JSON 格式节假日数据
- [x] 提供 REST API 查询服务
- [x] 支持 Docker 部署
- [ ] CI 自动更新
- [ ] 数据变化时自动发布新版本 ( `Watch` - `Release only` 以获取邮件提醒! )
- [ ] [发布页面]提供 JSON 打包下载

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

## iCalendar 订阅

网址格式参见上一节。

`{年份}.ics` 为对应年份的节假日，
`holiday-cn.ics` 为 3 年前至次年的节假日。

## 作为 git 子模块使用

参见 [Git 工具 - 子模块](https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E5%AD%90%E6%A8%A1%E5%9D%97)

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

```json
{
  "date": "2024-10-01",
  "isHoliday": true,
  "isOffDay": true,
  "name": "国庆节"
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

支持通过 Docker 部署数据更新和 API 查询服务。

### 使用 docker-compose

```bash
# 首次运行：获取所有历史数据
docker-compose run --rm update

# 启动 API 服务（常驻后台）
docker-compose up -d api

# 查看日志
docker-compose logs -f api
```

### 配置定时更新

在服务器上添加 cron 任务，定时更新数据：

```bash
# 编辑 crontab
crontab -e

# 每天中午 12 点更新数据
0 12 * * * cd /path/to/holiday-cn && docker-compose run --rm update
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MODE` | 运行模式：`api` 或 `update` | `api` |
| `UPDATE_ARGS` | 更新命令参数，如 `--all` | - |

[发布页面]: https://github.com/drjiathu/holiday-cn/releases
