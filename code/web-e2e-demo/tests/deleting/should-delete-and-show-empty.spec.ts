// spec: specs/todo.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('删除与空态', () => {
  test('should-delete-and-show-empty', async ({ page }) => {
    // 1. 添加"买牛奶"
    await page.getByRole('textbox', { name: '待办内容' }).fill('买牛奶');
    await page.getByRole('button', { name: '添加' }).click();

    // 2. 点击"删除：买牛奶"按钮
    await page.getByRole('button', { name: '删除：买牛奶' }).click();

    // expect: "暂无待办"空态可见
    await expect(page.getByText('暂无待办')).toBeVisible();
    // expect: 计数显示"共 0 项，未完成 0"
    await expect(page.getByText('共 0 项，未完成 0')).toBeVisible();
  });
});
