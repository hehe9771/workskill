# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: seed.spec.ts >> seed
- Location: tests\seed.spec.ts:3:5

# Error details

```
Error: coverage.stopJSCoverage: Target page, context or browser has been closed
```

# Test source

```ts
  1  | import { test as baseTest, expect } from '@playwright/test';
  2  | import { addCoverageReport } from 'monocart-reporter';
  3  | 
  4  | export { expect };
  5  | 
  6  | export const test = baseTest.extend({
  7  |   page: async ({ page, request }, use) => {
  8  |     // 场景隔离：通过真实 API 清空服务端待办（等价重置数据库，非 mock）
  9  |     const todos = (await (await request.get('/api/todos')).json()) as Array<{ id: number }>;
  10 |     for (const t of todos) {
  11 |       await request.delete(`/api/todos/${t.id}`);
  12 |     }
  13 | 
  14 |     // 所有窗口最大化：设备仿真项目 --start-maximized 不生效（device viewport 覆盖顶层 viewport:null，
  15 |     // Playwright 接管窗口尺寸），须 CDP 逐窗口强制最大化（实测 showCmd=3）。每个测试一个新窗口。
  16 |     const cdp = await page.context().newCDPSession(page);
  17 |     const { windowId } = await cdp.send('Browser.getWindowForTarget');
  18 |     await cdp.send('Browser.setWindowBounds', { windowId, bounds: { windowState: 'maximized' } });
  19 | 
  20 |     // V8 代码覆盖率收集（Chromium only；monocart coverage:true 仅开汇总，数据须在此收集）
  21 |     const isChromium = test.info().project.use?.defaultBrowserType === 'chromium';
  22 |     if (isChromium) {
  23 |       await Promise.all([
  24 |         page.coverage.startJSCoverage({ resetOnNavigation: false }),
  25 |         page.coverage.startCSSCoverage({ resetOnNavigation: false }),
  26 |       ]);
  27 |     }
  28 | 
  29 |     await page.goto('/');
  30 |     await use(page);
  31 | 
  32 |     if (isChromium) {
  33 |       const [jsCoverage, cssCoverage] = await Promise.all([
> 34 |         page.coverage.stopJSCoverage(),
     |                       ^ Error: coverage.stopJSCoverage: Target page, context or browser has been closed
  35 |         page.coverage.stopCSSCoverage(),
  36 |       ]);
  37 |       await addCoverageReport([...jsCoverage, ...cssCoverage], test.info());
  38 |     }
  39 |   },
  40 | });
  41 | 
```