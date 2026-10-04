// spec: specs/todo.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('导航', () => {
  test('should-switch-filter-by-hash', async ({ page }) => {
    // 1. 点击"未完成"过滤链接
    await page.getByRole('link', { name: '未完成' }).click();

    // expect: URL hash 为 #active
    await expect(page).toHaveURL(/#active$/);
    // expect: "未完成"链接处于激活态
    await expect(page.getByRole('link', { name: '未完成' })).toHaveClass(/active/);

    // 2. 直接导航到 /#done
    await page.goto('/#done');

    // expect: "已完成"链接处于激活态
    await expect(page.getByRole('link', { name: '已完成' })).toHaveClass(/active/);
  });
});
