// spec: specs/todo.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('添加与校验', () => {
  test('should-reject-empty-input', async ({ page }) => {
    // 1. 输入框留空，直接点击"添加"按钮
    await page.getByRole('button', { name: '添加' }).click();

    // expect: alert 元素可见，文本"请输入内容"
    await expect(page.getByRole('alert')).toBeVisible();
    await expect(page.getByRole('alert')).toHaveText('请输入内容');
    // expect: 列表仍为空（"暂无待办"可见）
    await expect(page.getByText('暂无待办')).toBeVisible();
  });
});
