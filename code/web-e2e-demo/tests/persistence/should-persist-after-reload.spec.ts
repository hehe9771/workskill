// spec: specs/todo.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('持久化（真实 API 往返）', () => {
  test('should-persist-after-reload', async ({ page }) => {
    // 1. 添加"买牛奶"、"记笔记"
    await page.getByRole('textbox', { name: '待办内容' }).fill('买牛奶');
    await page.getByRole('button', { name: '添加' }).click();
    await page.getByRole('textbox', { name: '待办内容' }).fill('记笔记');
    await page.getByRole('button', { name: '添加' }).click();

    // 2. 重新加载页面
    await page.reload();

    // expect: 列表仍显示"买牛奶"与"记笔记"（数据来自真实 API，非前端缓存）
    await expect(page.getByRole('listitem').filter({ hasText: '买牛奶' })).toBeVisible();
    await expect(page.getByRole('listitem').filter({ hasText: '记笔记' })).toBeVisible();
    await expect(page.getByText('共 2 项，未完成 2')).toBeVisible();
  });
});
