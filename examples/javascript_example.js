/**
 * 通过 jsDelivr CDN 访问中国法定节假日数据的 JavaScript 示例
 *
 * CDN 地址格式:
 * https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/{year}.json
 *
 * 适用于: Node.js (18+) 和现代浏览器
 */

// CDN 基础地址 (使用 @latest 自动指向最新 release)
const CDN_BASE_URL =
  "https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data";

// 内存缓存
const cache = new Map();

/**
 * 获取指定年份的节假日数据（带缓存）
 * @param {number} year - 年份
 * @returns {Promise<Object>} 节假日数据
 */
async function getHolidays(year) {
  if (cache.has(year)) {
    return cache.get(year);
  }

  const url = `${CDN_BASE_URL}/${year}.json`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch holidays for ${year}: ${response.status}`);
  }

  const data = await response.json();
  cache.set(year, data);
  return data;
}

/**
 * 检查某天是否为法定节假日
 * @param {string} queryDate - 日期，格式为 "YYYY-MM-DD"
 * @returns {Promise<Object>} 节假日信息
 */
async function isHoliday(queryDate) {
  const year = parseInt(queryDate.slice(0, 4));
  const data = await getHolidays(year);

  const day = data.days.find((d) => d.date === queryDate);

  if (day) {
    return {
      date: queryDate,
      isHoliday: true,
      isOffDay: day.isOffDay,
      name: day.name,
    };
  }

  return { date: queryDate, isHoliday: false };
}

/**
 * 判断是否为休息日（法定节假日且放假）
 * @param {string} queryDate - 日期
 * @returns {Promise<boolean>}
 */
async function isOffDay(queryDate) {
  const result = await isHoliday(queryDate);
  return result.isOffDay ?? false;
}

/**
 * 判断是否为调休工作日
 * @param {string} queryDate - 日期
 * @returns {Promise<boolean>}
 */
async function isWorkDay(queryDate) {
  const result = await isHoliday(queryDate);
  return result.isHoliday && !result.isOffDay;
}

/**
 * 获取日期范围内的所有节假日
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise<Array>}
 */
async function getHolidaysInRange(startDate, endDate) {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const startYear = start.getFullYear();
  const endYear = end.getFullYear();

  const results = [];

  for (let year = startYear; year <= endYear; year++) {
    const data = await getHolidays(year);
    for (const day of data.days) {
      const dayDate = new Date(day.date);
      if (dayDate >= start && dayDate <= end) {
        results.push(day);
      }
    }
  }

  return results;
}

/**
 * 获取下一个法定假日
 * @param {Date|string} fromDate - 起始日期，默认今天
 * @returns {Promise<Object|null>}
 */
async function getNextHoliday(fromDate = new Date()) {
  if (typeof fromDate === "string") {
    fromDate = new Date(fromDate);
  }

  const currentYear = fromDate.getFullYear();

  for (const year of [currentYear, currentYear + 1]) {
    try {
      const data = await getHolidays(year);
      for (const day of data.days) {
        const dayDate = new Date(day.date);
        if (dayDate > fromDate && day.isOffDay) {
          return day;
        }
      }
    } catch {
      continue;
    }
  }

  return null;
}

// ============ 使用示例 ============

async function main() {
  console.log("=".repeat(50));
  console.log("中国法定节假日查询示例 (JavaScript)");
  console.log("=".repeat(50));

  // 示例 1: 查询特定日期
  console.log("\n1. 查询特定日期是否为节假日:");
  let result = await isHoliday("2024-10-01");
  console.log(`   2024-10-01:`, result);

  result = await isHoliday("2024-10-08");
  console.log(`   2024-10-08:`, result);

  // 示例 2: 判断是否为休息日
  console.log("\n2. 判断是否为休息日:");
  console.log(`   2024-10-01 是休息日: ${await isOffDay("2024-10-01")}`);
  console.log(`   2024-09-29 是休息日: ${await isOffDay("2024-09-29")}`);

  // 示例 3: 判断是否为调休工作日
  console.log("\n3. 判断是否为调休工作日:");
  console.log(`   2024-09-29 是调休工作日: ${await isWorkDay("2024-09-29")}`);

  // 示例 4: 获取日期范围内的节假日
  console.log("\n4. 获取 2024 年 10 月的节假日:");
  const holidays = await getHolidaysInRange("2024-10-01", "2024-10-31");
  for (const h of holidays) {
    const status = h.isOffDay ? "休息" : "上班";
    console.log(`   ${h.date} ${h.name} (${status})`);
  }

  // 示例 5: 获取下一个假日
  console.log("\n5. 获取下一个假日:");
  const nextHoliday = await getNextHoliday();
  if (nextHoliday) {
    console.log(`   ${nextHoliday.date} ${nextHoliday.name}`);
  }

  // 示例 6: 获取年度数据概览
  console.log("\n6. 2024 年节假日概览:");
  const data = await getHolidays(2024);
  console.log(`   数据来源: ${data.papers[0].slice(0, 50)}...`);
  const offDays = data.days.filter((d) => d.isOffDay);
  const workDays = data.days.filter((d) => !d.isOffDay);
  console.log(`   放假天数: ${offDays.length} 天`);
  console.log(`   调休天数: ${workDays.length} 天`);
}

// 运行示例
main().catch(console.error);

// 导出函数 (用于模块化使用)
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    getHolidays,
    isHoliday,
    isOffDay,
    isWorkDay,
    getHolidaysInRange,
    getNextHoliday,
  };
}
