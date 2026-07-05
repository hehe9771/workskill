# PetPal Mobile App 架构专家评审报告

> 评审对象：`D:\mydoc\mysaasone\mysaas\mobile-app`
> 技术栈：React Native 0.76.9 + Expo 56 + TypeScript 5.0
> 源文件：205 个 .ts/.tsx，总计 ~25,800 行
> 评审日期：2026-07-03

---

## 一、整体评分

| 维度 | 满分 | 得分 | 说明 |
|------|------|------|------|
| 架构设计 | 25 | 19 | Feature-based 分层清晰，但缺跨环境隔离与 token 自动刷新 |
| 组件质量 | 20 | 14 | 共享组件体系完整，但存在大文件超标、部分组件职责过重 |
| 代码质量 | 25 | 17 | 代码语义化好，但测试覆盖极低（10/205），多处硬编码 |
| 性能安全 | 20 | 13 | Sentry 集成到位，但 ErrorBoundary 未上报、生产 env 占位未填 |
| 工程规范 | 10 | 7 | Husky + lint-staged + 路径别名齐全，但双目录对称冗余 |
| **总分** | **100** | **70** | **等级：合格（C+），可上线但存在多处需修复的工程债务** |

---

## 二、整体结论

**等级判定：合格（偏良好），核心短板在安全配置和测试覆盖。**

### 核心优势
1. **Feature-based 架构成熟**：`src/features/` 按业务域拆分（auth/ai/calendar/family/pet…），每个 feature 内含 components/screens/hooks/stores/utils，高内聚低耦合
2. **Design Token 体系完整**：colors/spacing/typography/radii/shadows 全部分离，主题切换规范
3. **安全存储分层合理**：session token 存 Keychain（P0-2），内存缓存同步注入避免 race condition，注释详实记录了迁移根因
4. **API 层封装干净**：axios 拦截器区分后端请求与跨域上传，superjson 序列化/反序列化透明处理
5. **路径别名统一**：tsconfig + babel-plugin-module-resolver 双配置一致

### 核心短板
1. 生产环境配置未完成（API_BASE_URL 占位、Sentry DSN 为空）
2. 测试覆盖极低（仅 10 个测试文件 / 205 个源文件 ≈ 4.9%）
3. ErrorBoundary 捕获异常后未上报 Sentry，生产环境崩溃监控有盲区
4. mysaasone 与 mysaastow 完全对称的双目录，维护成本翻倍

---

## 三、问题清单（分级）

### 🔴 严重风险（必须修复，阻塞上线）

#### S-1. 生产环境 API_BASE_URL 为占位符
- **位置**：`.env.production:6`
- **问题**：`API_BASE_URL=https://PRODUCTION_API_HOST`，release 包所有请求将 Network Error
- **风险**：发布后 APP 完全不可用
- **修复**：替换为真实生产域名，或通过 CI 环境变量注入

#### S-2. ErrorBoundary 未上报 Sentry
- **位置**：`src/shared/components/ErrorBoundary.tsx:24-26`
- **问题**：`componentDidCatch` 只 `console.error`，未调用 `captureError`
- **风险**：生产环境渲染崩溃无法被监控捕获，用户看到白屏但后台无报警
- **修复**：
```tsx
import {captureError} from '@shared/utils/sentry';

componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
  captureError(error, `ErrorBoundary:${errorInfo.componentStack?.slice(0, 200)}`);
}
```

#### S-3. 双目录完全对称（mysaasone / mysaastow）
- **位置**：`D:\mydoc\mysaasone\` 与 `D:\mydoc\mysaastow\`
- **问题**：两个目录源码几乎一致，mysaasone 多出 ~19 个文件（calendar 通知/编辑等）
- **风险**：代码分叉失控，修复一处需同步另一处，维护成本翻倍
- **修复**：明确定义哪个是主仓库、哪个是环境副本。推荐单仓库 + git branch 管理多环境

#### S-4. Google OAuth Client ID 硬编码进 git
- **位置**：`.env.production:13`
- **问题**：`GOOGLE_WEB_CLIENT_ID=906442364223-...` 直接提交到仓库
- **风险**：虽 OAuth Web Client ID 非密钥，但硬编码导致换 ID 需发版；且与 .env.example 不一致（example 为空）
- **修复**：移至 CI 环境变量注入，.env.production 保留占位

### 🟡 一般问题（建议修复，影响可维护性）

#### M-1. 多文件超过 500 行上限
- **位置**：ProfileEditScreen(515行)、EditPetScreen(497行)、AddPetScreen(484行)、AddEventScreen(481行)、EventDetailScreen(456行)、ReminderModal(432行)
- **风险**：单文件过大，认知负荷高，违反项目自身 500 行规范
- **修复**：将表单验证逻辑、子组件、样式抽取到独立文件

#### M-2. 测试覆盖率严重不足
- **位置**：205 源文件 vs 10 测试文件
- **问题**：核心模块（authStore、apiClient、cacheManager、secureStorage）零测试
- **风险**：回归无防护网，认证/支付等核心流程无法验证
- **修复**：优先为 shared/api、shared/cache、features/auth/stores 补充单元测试

#### M-3. authStore.guestLogin 不持久化 session
- **位置**：`src/features/auth/stores/authStore.ts:251-262`
- **问题**：guestLogin 直接 set isAuthenticated=true，无 sessionId 写入 Keychain
- **风险**：APP 重启后 guest 状态丢失（restoreSession 无法恢复），且 guest 用户调用 API 时无 token 导致 401
- **修复**：要么为 guest 生成临时 token 持久化，要么在 restoreSession 中识别 guest 标记

#### M-4. apiClient 缺少 401 token 自动刷新机制
- **位置**：`src/shared/api/apiClient.ts:75-101`
- **问题**：响应拦截器未处理 401（session 过期），需用户重新登录
- **风险**：用户体验差 — 使用中 session 过期直接报错，无法无感刷新
- **修复**：添加 401 拦截 → 尝试 refreshToken → 重试原请求 → 失败才跳登录

#### M-5. MainTabNavigator 中 colors 变量解构但未使用
- **位置**：`src/app/navigation/MainTabNavigator.tsx:48,65,83,96,105`
- **问题**：HomeStackNavigator/AIStackNavigator 等多个函数中 `const {colors} = useTheme()` 被解构但未在 screenOptions 中使用
- **风险**：代码冗余，每次 theme 切换触发无意义重渲染
- **修复**：移除未使用的 colors 解构

#### M-6. authStore.signup 错误解析链过长且脆弱
- **位置**：`src/features/auth/stores/authStore.ts:106-114`
- **问题**：`resp?.data?.data?.message ?? resp?.data?.message ?? err.message` 三层 fallback 依赖后端精确结构
- **风险**：后端响应格式变更时错误信息丢失，用户看到 "Sign up failed" 而非具体原因
- **修复**：定义 `ApiErrorResponse` 类型，统一后端错误解析函数放 shared/utils

### 🟢 优化建议（迭代改进）

#### O-1. RootNavigator 双 NavigationContainer 切换导致 native stack 完全重建
- **位置**：`src/app/navigation/RootNavigator.tsx:43-55`
- **问题**：通过 key="auth"/"main" 强制重建，注释说明是为了解决 native 缓存 bug
- **优化**：考虑改用单 NavigationContainer + 条件 Screen（React Navigation 6+ 推荐模式），或在认证切换时 dispatch reset action

#### O-2. HomeScreen FlatList renderItem 内联奇偶判断
- **位置**：`src/features/home/screens/HomeScreen.tsx:233-253`
- **问题**：renderItem 内 `index % 2 === 0` 判断 CookieCard vs MochiCard
- **优化**：抽取 `renderPetCard(item, index)` 函数，或统一为 PetCard 组件 + variant prop

#### O-3. displayName 逻辑散落
- **位置**：`HomeScreen.tsx:67-71`
- **问题**：`user?.nickname || user?.username || user?.email?.split('@')[0] || 'Pet Parent'` 是通用逻辑
- **优化**：提取到 `shared/utils/userDisplayName.ts`，多处复用

#### O-4. TipBanner 硬编码文案
- **位置**：`HomeScreen.tsx:199-202`
- **问题**：`"Remember to deworm your pet today ~ Last deworming was 30 days ago"` 硬编码
- **优化**：从后端配置接口获取或本地化

---

## 四、针对性优化方案

### 方案 A：生产配置安全化（S-1/S-4，1天）

```bash
# .env.production — 替换占位
API_BASE_URL=https://api.petpal.com  # 替换为真实域名
GOOGLE_WEB_CLIENT_ID=  # 清空，CI 注入

# CI/CD 脚本 (e.g. appcenter-post-clone.sh)
echo "API_BASE_URL=$PRODUCTION_API_URL" > .env.production
echo "GOOGLE_WEB_CLIENT_ID=$GOOGLE_WEB_CLIENT_ID" >> .env.production
```

### 方案 B：ErrorBoundary 接入 Sentry（S-2，0.5天）

```tsx
// src/shared/components/ErrorBoundary.tsx
import {captureError} from '@shared/utils/sentry';

componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
  // 上报 Sentry（生产环境崩溃监控）
  captureError(error, `ErrorBoundary: ${errorInfo.componentStack?.split('\n').slice(1, 4).join(' <- ')}`);
}
```

### 方案 C：authStore guest 持久化（M-3，0.5天）

```ts
// authStore.ts — guestLogin 增加本地标记
guestLogin: () => {
  cacheManager.set(cacheKeys.session.biometric, {isGuest: true});
  set({
    user: {id: 'guest', email: 'guest@petpal.local', username: 'Guest'} as ApiUser,
    isAuthenticated: true,
    isLoading: false,
    error: null,
  });
},

// restoreSession 增加 guest 恢复
restoreSession: async () => {
  // ...existing Keychain logic...
  if (!sessionId) {
    const guestFlag = cacheManager.get<{isGuest: boolean}>(cacheKeys.session.biometric);
    if (guestFlag?.isGuest) {
      get().guestLogin();
      set({isLoading: false});
      return;
    }
  }
  // ...existing restore logic...
}
```

### 方案 D：401 Token 自动刷新（M-4，1天）

```ts
// apiClient.ts — 响应拦截器增加 401 处理
apiClient.interceptors.response.use(
  response => { /* existing */ },
  async error => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // 尝试用 refreshToken 或 restoreSession 获取新 token
        await useAuthStore.getState().restoreSession();
        if (apiTokenCache) {
          originalRequest.headers.Authorization = `Bearer ${apiTokenCache}`;
          return apiClient(originalRequest);
        }
      } catch {
        // 刷新失败，跳转登录
      }
    }
    return Promise.reject(error);
  }
);
```

### 方案 E：大文件拆分（M-1，2天）

以 ProfileEditScreen(515行) 为例：
```
features/profile-edit/
├── screens/ProfileEditScreen.tsx        ← 减至 ~200 行（仅布局）
├── components/AvatarPicker.tsx          ← 抽取头像选择（~80行）
├── components/ProfileForm.tsx           ← 抽取表单区域（~120行）
├── hooks/useProfileEdit.ts             ← 抽取表单逻辑+提交（~80行）
└── validation/profileSchema.ts          ← 抽取 zod schema（~30行）
```

---

## 五、长期架构优化建议

### 第一阶段（1-2周）：修复严重风险
- [ ] 替换 .env.production 占位，CI 注入敏感配置
- [ ] ErrorBoundary 接入 Sentry
- [ ] 统一 mysaasone/mysaastow 为单仓库多分支
- [ ] 补充 authStore + apiClient 单元测试

### 第二阶段（2-4周）：提升工程质量
- [ ] 拆分超 500 行的 6 个文件
- [ ] 实现 401 token 自动刷新
- [ ] 核心业务测试覆盖率达 60%+
- [ ] 清除未使用变量（colors 解构等）

### 第三阶段（1-2月）：架构升级
- [ ] 引入 React Query 管理服务端状态（已装 @tanstack/react-query 但未充分利用）
- [ ] 考虑引入 Zustand persist middleware 替代手动 cacheManager 同步
- [ ] 评估 New Architecture（Fabric + TurboModules）迁移计划
- [ ] 建立 E2E 测试（已有 Detox 配置但未启用核心流程测试）

---

## 附录：源码结构速览

```
src/
├── app/navigation/        # 路由定义（Root/Auth/MainTab/5 Stack）
├── features/              # 18 个业务模块
│   ├── auth/              # 认证（login/signup/google/biometric）
│   ├── ai/                # AI Hub + 7 子功能
│   ├── calendar/          # 日历事件 + 提醒
│   ├── family/            # 家庭组管理
│   ├── home/              # 首页
│   ├── pet/ / pets/       # 宠物列表
│   ├── pet-profile/       # 宠物详情（体重图表）
│   ├── profile/           # 个人中心
│   ├── profile-edit/      # 编辑资料
│   ├── settings/          # 设置
│   └── ...（12 更多模块）
├── shared/                # 公共层
│   ├── api/               # apiClient + endpoints + superjson
│   ├── cache/             # MMKV cacheManager + cacheKeys
│   ├── components/        # 15 个共享 UI 组件
│   ├── hooks/             # 通用 hooks（网络/动画/Tab导航）
│   ├── utils/             # sentry / secureStorage / weightConvert
│   └── validation/        # zod schemas
├── theme/                 # ThemeContext（light/dark）
├── tokens/                # Design Tokens（colors/spacing/typography/radii/shadows）
└── types/                 # 全局类型定义（api/navigation）
```
