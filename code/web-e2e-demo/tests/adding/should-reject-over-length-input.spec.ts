// spec: specs/todo.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('添加与校验', () => {
  test('should-reject-over-length-input', async ({ page }) => {
    // 1. 输入 201 个字符
    await page.getByRole('textbox', { name: '待办内容' }).fill('a'.repeat(201));

    // 2. 点击"添加"按钮
    await page.getByRole('button', { name: '添加' }).click();

    // expect: alert 元素可见，文本"内容不能超过 200 字"
    await expect(page.getByRole('alert')).toBeVisible();
    await expect(page.getByRole('alert')).toHaveText('内容不能超过 200 字');
  });
});
