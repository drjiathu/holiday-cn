# holiday-cn

中国法定节假日数据，每日自动抓取国务院公告。

- [x] 提供 JSON 格式节假日数据
- [x] 提供数据打包下载 
- [ ] CI 自动更新
- [ ] 根据变化时自动发布新版本( `Watch` - `Release only` 以获取邮件提醒! )
- [ ] 数据自动同步保存至 `MongoDB` 数据库

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

- 年份是按照国务院文件标题年份而不是日期年份，12 月份的日期可能会被下一年的文件影响，因此应检查两个文件。

## iCalendar 订阅

网址格式参见上一节。

`{年份}.ics` 为对应年份的节假日，
`holiday-cn.ics` 为 3 年前至次年的节假日。

## 作为 git 子模块使用

参见 [Git 工具 - 子模块](https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E5%AD%90%E6%A8%A1%E5%9D%97)

[发布页面]: https://github.com/drjiathu/holiday-cn/releases