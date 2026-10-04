// spec: specs/todo.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('添加与校验', () => {
  test('should-add-single-todo', async ({ page }) => {
    const input = page.getByRole('textbox', { name: '待办内容' });

    // 1. 在"待办内容"输入框输入"买牛奶"
    await input.fill('买牛奶');
    await expect(input).toHaveValue('买牛奶');

    // 2. 点击"添加"按钮
    await page.getByRole('button', { name: '添加' }).click();

    // expect: 列表出现 listitem，含文本"买牛奶"
    await expect(page.getByRole('listitem').filter({ hasText: '买牛奶' })).toBeVisible();
    // expect: 计数显示"共 1 项，未完成 1"
    await expect(page.getByText('共 1 项，未完成 1')).toBeVisible();
  });
});
