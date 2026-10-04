// keep-open 收尾测试：E2E_KEEP_OPEN=1 时在全部场景跑完后保留浏览器窗口供用户查看。
// 文件名 zz- 前缀保证字母序最后执行；不经过 fixtures（避免场景隔离清空前一个测试留下的最终状态）。
import { test, expect } from '@playwright/test';

test('keep-open', async ({ page }) => {
  test.skip(
    !process.env.E2E_KEEP_OPEN,
    'keep-open 仅在 E2E_KEEP_OPEN=1 时运行：测试结束后保留浏览器窗口供用户查看'
  );
  await page.goto('/');
  await expect(page.getByRole('heading', { name: '待办清单' })).toBeVisible();
  // 设备仿真项目下 --start-maximized 不生效：device viewport（412×915）覆盖顶层 viewport:null，
  // Playwright 转而接管窗口尺寸（实测 showCmd=1，1265×1372 非最大化）。
  // 用 CDP 强制最大化窗口（实测 showCmd=3），移动仿真视口不受影响。
  const session = await page.context().newCDPSession(page);
  const { windowId } = await session.send('Browser.getWindowForTarget');
  await session.send('Browser.setWindowBounds', { windowId, bounds: { windowState: 'maximized' } });
  // 挂住窗口：用户在 Playwright Inspector 点“继续”或直接关闭窗口/会话时结束
  await page.pause();
});
