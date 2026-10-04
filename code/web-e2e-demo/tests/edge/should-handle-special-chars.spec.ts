// spec: specs/todo.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('边界值', () => {
  test('should-handle-special-chars', async ({ page }) => {
    const raw = '<b>bold</b> & "quotes" <script>alert(1)</script>';

    // 1. 添加文本 <b>bold</b> & "quotes" <script>alert(1)</script>
    await page.getByRole('textbox', { name: '待办内容' }).fill(raw);
    await page.getByRole('button', { name: '添加' }).click();

    // expect: listitem 的 title 属性含完整原文（textContent 渲染，未被当作 HTML 执行）
    const item = page.getByRole('listitem').filter({ hasText: 'bold' });
    await expect(item).toBeVisible();
    await expect(item.locator('span')).toHaveAttribute('title', raw);
  });
});
