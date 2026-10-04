// spec: specs/todo.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('勾选与过滤', () => {
  test('should-toggle-and-filter-done', async ({ page }) => {
    // 1. 添加"买牛奶"
    await page.getByRole('textbox', { name: '待办内容' }).fill('买牛奶');
    await page.getByRole('button', { name: '添加' }).click();

    // 2. 勾选"完成：买牛奶"复选框
    await page.getByRole('checkbox', { name: '完成：买牛奶' }).check();

    // expect: 计数显示"共 1 项，未完成 0"
    await expect(page.getByText('共 1 项，未完成 0')).toBeVisible();

    // 3. 点击"已完成"过滤链接
    await page.getByRole('link', { name: '已完成' }).click();

    // expect: URL hash 为 #done
    await expect(page).toHaveURL(/#done$/);
    // expect: 列表仍显示"买牛奶"（已完成的项）
    await expect(page.getByRole('listitem').filter({ hasText: '买牛奶' })).toBeVisible();
  });
});
