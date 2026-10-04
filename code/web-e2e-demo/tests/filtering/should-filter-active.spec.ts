// spec: specs/todo.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('勾选与过滤', () => {
  test('should-filter-active', async ({ page }) => {
    // 1. 添加"任务A"、"任务B"
    await page.getByRole('textbox', { name: '待办内容' }).fill('任务A');
    await page.getByRole('button', { name: '添加' }).click();
    await page.getByRole('textbox', { name: '待办内容' }).fill('任务B');
    await page.getByRole('button', { name: '添加' }).click();

    // 2. 勾选"完成：任务A"
    await page.getByRole('checkbox', { name: '完成：任务A' }).check();

    // 3. 点击"未完成"过滤链接
    await page.getByRole('link', { name: '未完成' }).click();

    // expect: URL hash 为 #active
    await expect(page).toHaveURL(/#active$/);
    // expect: 列表只显示"任务B"，不显示"任务A"
    await expect(page.getByRole('listitem').filter({ hasText: '任务B' })).toBeVisible();
    await expect(page.getByRole('listitem').filter({ hasText: '任务A' })).toHaveCount(0);
  });
});
