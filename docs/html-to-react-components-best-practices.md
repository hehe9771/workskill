# html-to-react-components 最佳实践

> 将 HTML 页面一键拆分为类型安全的 React 组件树

---

## 目录

1. [项目简介](#项目简介)
2. [安装](#安装)
3. [核心原理](#核心原理)
4. [人工使用流程](#人工使用流程)
5. [Claude Code 自动化使用流程](#claude-code-自动化使用流程)
6. [最佳实践](#最佳实践)
7. [常见问题排查](#常见问题排查)
8. [与 html-react-parser 对比选型](#与-html-react-parser-对比选型)

---

## 项目简介

| 属性 | 值 |
|------|------|
| 仓库 | [roman01la/html-to-react-components](https://github.com/roman01la/html-to-react-components) |
| 星标 | 2,177+ |
| 许可证 | MIT |
| Node 版本要求 | >= 18 |
| 默认输出 | TypeScript (`.tsx`) |

**核心价值**：设计师交付的 HTML 文件，通过简单标注 `data-component` 和 `public:` 属性，一键生成完整的 React 组件文件树，省去手动拆分的重复劳动。

**适用场景**：遗留 HTML 页面/模板迁移到 React 项目。

---

## 安装

### 全局安装（推荐）

```bash
npm i -g html-to-react-components
```

### 项目本地安装

```bash
npm install --save-dev html-to-react-components
```

本地安装后通过 npx 调用：

```bash
npx html-to-react-components "./src/**/*.html"
```

---

## 核心原理

工具通过两个标注约定工作：

| 标注 | 作用 | 示例 |
|------|------|------|
| `data-component="ComponentName"` | 将元素及其子元素提取为独立组件 | `<div data-component="Header">...</div>` |
| `public:attr="value"` | 将该属性暴露为 React props | `<input public:type="text" data-component="Input" />` |

**转换示例**：

```html
<!-- 输入 HTML -->
<input public:type="text" public:placeholder="请输入" id="search" data-component="Input" />
```

```tsx
// 输出 components/Input.tsx
interface InputProps {
  type: string;
  placeholder: string;
}

const Input = ({ type, placeholder }: InputProps) => (
  <input type={type} placeholder={placeholder} id="search" />
);

export default Input;

// 使用处
<Input type="text" placeholder="请输入" />
```

---

## 人工使用流程

### Step 1：准备 HTML 文件

拿到设计师或后端提供的 HTML 文件，例如 `index.html`：

```html
<!DOCTYPE html>
<html>
<body>
  <header class="header">
    <h1 class="heading">欢迎使用</h1>
    <nav class="nav">
      <ul class="list">
        <li class="list-item">首页</li>
        <li class="list-item">产品</li>
        <li class="list-item">联系</li>
      </ul>
    </nav>
  </header>
  <main class="content">
    <p>页面内容...</p>
  </main>
  <footer class="footer">
    <p>Copyright 2026</p>
  </footer>
</body>
</html>
```

### Step 2：标注 data-component 和 public: 属性

分析页面结构，决定拆分粒度。原则：

- **独立的 UI 区域** → 加 `data-component`
- **需要外部传入的动态值** → 加 `public:` 前缀
- **静态不变的的属性** → 不加 `public:`，保留为组件内部固定属性

标注后的 HTML：

```html
<!DOCTYPE html>
<html>
<body>
  <header class="header" data-component="Header">
    <h1 public:title="欢迎使用" class="heading" data-component="Heading" />
    <nav class="nav" data-component="Nav">
      <ul class="list">
        <li public:text="首页" class="list-item" data-component="ListItem" />
        <li public:text="产品" class="list-item" data-component="ListItem" />
        <li public:text="联系" class="list-item" data-component="ListItem" />
      </ul>
    </nav>
  </header>
  <main class="content" data-component="Main">
    <p>页面内容...</p>
  </main>
  <footer class="footer" data-component="Footer">
    <p public:copyright="Copyright 2026" />
  </footer>
</body>
</html>
```

### Step 3：执行转换

```bash
html2react "./index.html"
```

默认在 `./components/` 目录下生成：

```
components/
├── Header.tsx
├── Heading.tsx
├── Nav.tsx
├── ListItem.tsx
├── Main.tsx
└── Footer.tsx
```

### Step 4：查看生成结果

每个组件文件类似：

```tsx
// Header.tsx
import React from "react";
import Heading from "./Heading";
import Nav from "./Nav";

const Header = () => (
  <header className="header">
    <Heading />
    <Nav />
  </header>
);

export default Header;
```

### Step 5：集成到 React 项目

```tsx
// App.tsx
import Header from "./components/Header";
import Main from "./components/Main";
import Footer from "./components/Footer";

function App() {
  return (
    <>
      <Header />
      <Main />
      <Footer />
    </>
  );
}

export default App;
```

---

## CLI 选项速查

```bash
html2react "./src/**/*.html" [选项]
```

| 选项 | 简写 | 说明 | 默认值 | 可选值 |
|------|------|------|--------|--------|
| `--component` | `-c` | 组件类型 | `functional` | `functional`, `class`, `es5` |
| `--module` | `-m` | 模块格式 | `es` | `es`, `cjs` |
| `--typescript` | `-t` | 输出 TypeScript | `true` | 布尔值，用 `--no-typescript` 关闭 |
| `--out` | `-o` | 输出目录 | `./components` | 任意路径 |
| `--ext` | `-e` | 文件扩展名 | `tsx` | `tsx`, `jsx`, `js` |
| `--delimiter` | `-d` | 文件名分隔符 | 无 | `-`, `_` 等 |

**常用组合**：

```bash
# 生成 JavaScript class 组件到 src/ 目录
html2react "./index.html" -c class -m es --no-typescript -o ./src/components

# 生成带分隔符文件名的组件（如 Header 输出为 header.tsx）
html2react "./index.html" -d "-"

# 批量处理所有 HTML 文件
html2react "./src/**/*.html" -o ./react-components
```

---

## Node.js API 用法

适合集成到构建脚本或自动化流程中：

```js
const extractReactComponents = require("html-to-react-components");
const fs = require("fs");
const path = require("path");

async function convertHtmlToReact(htmlFilePath) {
  const html = fs.readFileSync(htmlFilePath, "utf-8");

  const components = await extractReactComponents(html, {
    componentType: "functional",
    moduleType: "es",
    typescript: true,
    output: {
      path: "./components",
      fileExtension: "tsx",
    },
  });

  // components 是 { ComponentName: fileContent } 对象
  for (const [name, content] of Object.entries(components)) {
    const outputPath = path.join("./components", `${name}.tsx`);
    fs.writeFileSync(outputPath, content, "utf-8");
    console.log(`Generated: ${outputPath}`);
  }
}

convertHtmlToReact("./index.html");
```

---

## Claude Code 自动化使用流程

### 场景 1：将现有 HTML 文件转换为 React 组件

直接在 Claude Code 对话中执行：

```
user: 把 ./templates/admin.html 转换为 React 组件，输出到 src/components/admin/
```

Claude Code 会：

1. 读取 HTML 文件
2. 分析页面结构，自动标注 `data-component` 和 `public:` 属性
3. 写入标注后的 HTML 临时文件
4. 执行 `html2react` 命令生成组件
5. 将生成的组件文件移动到目标目录
6. 创建 `App.tsx` 入口文件整合所有组件

### 场景 2：批量转换多个 HTML 文件

```
user: 把 ./templates/ 目录下所有 HTML 文件都转换为 React 组件
```

Claude Code 会：

1. 列出所有 HTML 文件
2. 逐个分析结构并自动标注
3. 执行批量转换
4. 整理输出目录结构

### 场景 3：标注现有 HTML 文件（不执行转换）

```
user: 帮我分析 admin.html 的结构，标注出适合拆分为 React 组件的部分
```

Claude Code 会：

1. 读取 HTML 文件
2. 识别独立 UI 区块
3. 识别可参数化的属性
4. 输出标注后的 HTML 供你审查

### 场景 4：自定义组件拆分策略

```
user: 将 index.html 转换为 React 组件，要求：
  1. Header 中的导航项从 props 传入，不要拆成独立组件
  2. Footer 保持完整不拆分
  3. 输出 JavaScript 而不是 TypeScript
```

Claude Code 会根据你的要求调整标注策略并执行转换。

### Claude Code 自动化标注脚本

可以在项目中创建转换脚本：

```js
// scripts/convert-html-to-react.js
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const INPUT_DIR = "./templates";
const OUTPUT_DIR = "./src/components/generated";

// 确保输出目录存在
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

// 获取所有 HTML 文件
const htmlFiles = fs.readdirSync(INPUT_DIR).filter(f => f.endsWith(".html"));

for (const file of htmlFiles) {
  const inputPath = path.join(INPUT_DIR, file);
  console.log(`Converting: ${file}`);

  try {
    execSync(`npx html-to-react-components "${inputPath}" -o "${OUTPUT_DIR}"`, {
      stdio: "inherit",
    });
  } catch (err) {
    console.error(`Failed to convert ${file}:`, err.message);
  }
}

console.log("Done!");
```

然后在 `package.json` 中添加脚本：

```json
{
  "scripts": {
    "convert:html": "node scripts/convert-html-to-react.js"
  }
}
```

运行：

```bash
npm run convert:html
```

---

## 最佳实践

### 1. 标注策略

#### 拆分粒度

| 场景 | 建议 |
|------|------|
| 大型区块（header, sidebar, footer） | 拆分为独立组件 |
| 重复元素（列表项、卡片） | 拆分为组件，通过 props 传入内容 |
| 简单单行元素 | 不拆分，保留在父组件内 |
| 纯样式容器（`<div class="wrapper">`） | 不拆分，合并到父组件 |

#### props 设计

```html
<!-- 好的做法：只暴露真正需要外部控制的属性 -->
<img public:src="/logo.png" public:alt="Logo" class="logo" data-component="Logo" />

<!-- 不好的做法：暴露所有属性，失去组件封装意义 -->
<img public:src="/logo.png" public:alt="Logo" public:class="logo" public:width="100" data-component="Logo" />
```

#### 避免过度标注

```html
<!-- 不好：每个元素都标，组件树过深 -->
<div data-component="Container">
  <div data-component="Row">
    <div data-component="Col">
      <p data-component="Text">内容</p>
    </div>
  </div>
</div>

<!-- 好：按语义区域拆分 -->
<div data-component="Container">
  <div class="row">
    <div class="col">
      <p>内容</p>
    </div>
  </div>
</div>
```

### 2. 命名规范

- 组件名使用 PascalCase：`Header`, `NavItem`, `UserProfile`
- 文件名使用连字符分隔（通过 `--delimiter` 选项）：`header.tsx`, `nav-item.tsx`

```bash
html2react "./index.html" -d "-"
# Header 组件输出为 header.tsx
# NavItem 组件输出为 nav-item.tsx
```

### 3. 生成后检查清单

转换完成后，逐项检查：

- [ ] 组件名是否正确（避免 `Div`, `Span` 等无意义命名）
- [ ] props 是否只暴露了需要动态传入的值
- [ ] `className` 是否正确替换了 `class`
- [ ] `style` 属性是否正确转为对象格式
- [ ] 组件间 import 路径是否正确
- [ ] 是否缺少必要的 `key` prop（列表渲染场景）
- [ ] 内联事件（`onclick`）已手动改为 React 事件处理

### 4. 与 CSS 配合使用

转换后 `className` 保留不变，需要确保 CSS 文件可被引用：

```tsx
// 方式 1：在全局样式中引入
import "./styles/global.css";

// 方式 2：每个组件引入自己的样式
import "./Header.css";
```

如果 CSS 也需要拆分，可以在转换后手动将相关样式移到对应组件的 CSS 文件中。

### 5. 处理内联样式

HTML 中的内联 `style` 属性在转换后保持字符串形式，需要手动改为对象：

```tsx
// 生成结果（不正确）
<div style="background: #fff; color: red;" />

// 需要改为
<div style={{ background: "#fff", color: "red" }} />
```

可以配合 Claude Code 批量修复：

```
user: 把所有生成组件中的 style="..." 改为 style={{ ... }} 对象格式
```

### 6. 处理列表渲染

相同 `data-component` 名的多个元素会生成同一个组件文件，但使用处需要手动加 `key`：

```tsx
// 生成结果
<ListItem text="首页" />
<ListItem text="产品" />
<ListItem text="联系" />

// 改为 map 渲染
{items.map((item, index) => (
  <ListItem key={index} text={item.text} />
))}
```

---

## 常见问题排查

### Q1：运行 `html2react` 报 `command not found`

**原因**：未全局安装或 npx 路径问题

```bash
# 确认全局安装
npm list -g html-to-react-components

# 使用 npx 替代直接调用
npx html-to-react-components "./index.html"
```

### Q2：生成的组件包含 `class` 而非 `className`

**原因**：旧版本行为，确保使用最新版本

```bash
npm update -g html-to-react-components
```

### Q3：组件嵌套关系不正确

**原因**：HTML 结构不规范（如未闭合标签）

检查 HTML 是否有效，可用 https://validator.w3.org/ 验证。

### Q4：TypeScript 类型报错

确保项目配置了正确的 TypeScript 版本（>= 4.0）：

```bash
npm install --save-dev typescript@latest
```

### Q5：生成文件为空或报错

检查 HTML 文件中是否包含 `data-component` 标注。没有任何标注的 HTML 不会生成组件。

### Q6：`<script>` 或 `<style>` 标签处理

这些标签的内容会保留在组件内，但不会自动执行。需要：

- `<style>` → 提取到独立 `.css` 文件
- `<script>` → 转换为 React `useEffect` 或事件处理

---

## 与 html-react-parser 对比选型

| 维度 | html-to-react-components | html-react-parser |
|------|--------------------------|-------------------|
| **本质** | 构建时工具（生成文件） | 运行时库（解析字符串） |
| **产物** | `.tsx` / `.js` 组件文件 | 内存中的 React 元素 |
| **适用场景** | 静态 HTML 迁移、设计师交付页面 | 富文本渲染、CMS 内容、动态 HTML |
| **是否需要标注** | 是（`data-component` + `public:`） | 否（直接解析） |
| **生成的组件可编辑** | 是（独立文件，可随意修改） | 否（运行时动态生成） |
| **性能** | 一次性转换，之后走 React 正常渲染 | 每次渲染都需解析 HTML 字符串 |
| **类型安全** | 是（自动生成 TypeScript 接口） | 是（TypeScript 项目） |
| **XSS 风险** | 无（转换为静态组件） | 有（需手动消毒） |

**选型决策**：

- HTML 页面**一次性迁移**到 React → 选 **html-to-react-components**
- 运行时**动态渲染 HTML 内容**（富文本、API 返回） → 选 **html-react-parser**
- 两者可**配合使用**：先用 html-to-react-components 迁移主体页面，再用 html-react-parser 渲染富文本内容区域
