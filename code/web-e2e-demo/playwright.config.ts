import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  retries: 0,
  workers: 1, // 共享内存后端：必须串行，否则 fixture 清空与并行 worker 竞态互污染
  reporter: [
    ['list'],
    ['monocart-reporter', {
      coverage: {
        reports: ['v8', 'json-summary', 'console-details'],
        entryFilter: () => true,
        sourceFilter: () => true,
      },
    }],
  ],
  use: {
    baseURL: 'http://localhost:3456',
    // 前台可见由全局机器强制保证：hook 强制 playwright test 命令带 --headed（CLI flag 覆盖任何 config，零项目设置）
    // 窗口最大化：viewport:null（视口=窗口实际尺寸）+ --start-maximized（Chromium 启动参数）
    viewport: null,
    launchOptions: { args: ['--start-maximized'] },
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    actionTimeout: 10000,
  },
  // 移动仿真：技能要求被测为移动设备，仿真在 project 层配置才对断言阶段生效
  projects: [
    { name: 'mobile-chrome', use: { ...devices['Pixel 7'] } },
  ],
  webServer: {
    command: 'node server.js',
    url: 'http://localhost:3456',
    reuseExistingServer: true,
    timeout: 30000,
  },
});
