import { test as baseTest, expect } from '@playwright/test';
import { addCoverageReport } from 'monocart-reporter';

export { expect };

export const test = baseTest.extend({
  page: async ({ page, request }, use) => {
    // 场景隔离：通过真实 API 清空服务端待办（等价重置数据库，非 mock）
    const todos = (await (await request.get('/api/todos')).json()) as Array<{ id: number }>;
    for (const t of todos) {
      await request.delete(`/api/todos/${t.id}`);
    }

    // 所有窗口最大化：设备仿真项目 --start-maximized 不生效（device viewport 覆盖顶层 viewport:null，
    // Playwright 接管窗口尺寸），须 CDP 逐窗口强制最大化（实测 showCmd=3）。每个测试一个新窗口。
    const cdp = await page.context().newCDPSession(page);
    const { windowId } = await cdp.send('Browser.getWindowForTarget');
    await cdp.send('Browser.setWindowBounds', { windowId, bounds: { windowState: 'maximized' } });

    // V8 代码覆盖率收集（Chromium only；monocart coverage:true 仅开汇总，数据须在此收集）
    const isChromium = test.info().project.use?.defaultBrowserType === 'chromium';
    if (isChromium) {
      await Promise.all([
        page.coverage.startJSCoverage({ resetOnNavigation: false }),
        page.coverage.startCSSCoverage({ resetOnNavigation: false }),
      ]);
    }

    await page.goto('/');
    await use(page);

    if (isChromium) {
      const [jsCoverage, cssCoverage] = await Promise.all([
        page.coverage.stopJSCoverage(),
        page.coverage.stopCSSCoverage(),
      ]);
      await addCoverageReport([...jsCoverage, ...cssCoverage], test.info());
    }
  },
});
