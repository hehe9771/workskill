import { test } from './fixtures';

test('seed', async ({ page }) => {
  // seed 仅供 agent 探索会话使用：E2E_EXPLORE=1 时 pause 保持会话存活，常规跑自动跳过
  test.skip(!process.env.E2E_EXPLORE, 'seed 仅用于 agent 探索会话（E2E_EXPLORE=1）');
  await page.pause();
});
