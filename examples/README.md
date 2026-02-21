# 使用示例

通过 jsDelivr CDN 免费访问中国法定节假日数据。

## CDN 地址

使用 `@latest` 自动指向最新 release 版本：

```
https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/{year}.json
https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/{year}.ics
```

## 示例文件

| 文件 | 说明 | 运行方式 |
|------|------|----------|
| [python_example.py](./python_example.py) | Python 示例 | `python python_example.py` |
| [javascript_example.js](./javascript_example.js) | Node.js 示例 | `node javascript_example.js` |
| [browser_example.html](./browser_example.html) | 浏览器示例 | 直接用浏览器打开 |
| [curl_example.sh](./curl_example.sh) | Shell/Curl 示例 | `bash curl_example.sh` |

## 快速开始

### Python

```python
import requests

def is_holiday(date: str) -> dict:
    year = date[:4]
    url = f"https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/{year}.json"
    data = requests.get(url).json()
    for day in data["days"]:
        if day["date"] == date:
            return {"isHoliday": True, **day}
    return {"isHoliday": False}

print(is_holiday("2024-10-01"))
# {'isHoliday': True, 'name': '国庆节', 'date': '2024-10-01', 'isOffDay': True}
```

### JavaScript

```javascript
async function isHoliday(date) {
  const year = date.slice(0, 4);
  const url = `https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/${year}.json`;
  const data = await fetch(url).then(r => r.json());
  const day = data.days.find(d => d.date === date);
  return day ? { isHoliday: true, ...day } : { isHoliday: false };
}

isHoliday("2024-10-01").then(console.log);
// {isHoliday: true, name: '国庆节', date: '2024-10-01', isOffDay: true}
```

### Curl

```bash
# 获取 2024 年数据
curl -s https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/2024.json

# 使用 jq 查询特定日期
curl -s https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/2024.json | \
  jq '.days[] | select(.date == "2024-10-01")'
```

## 注意事项

1. `@latest` 自动指向最新 release，发布新版本后会自动更新
2. 如需指定版本，可使用具体标签如 `@2024.02.21`
3. 数据范围: 2007 年至今
