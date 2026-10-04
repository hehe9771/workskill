# 待办清单 Test Plan

## Application Overview

移动端待办清单 demo：真实 fetch 调用内存 API（/api/todos），支持添加、勾选完成、删除、按状态过滤（URL hash 驱动）、超长与空输入校验。无任何 mock——测试全部打真实后端。

## Test Scenarios

### 1. 添加与校验

**Seed:** `tests/seed.spec.ts`

#### 1.1 should-add-single-todo

**File:** `tests/adding/should-add-single-todo.spec.ts`

**Steps:**
  1. 在"待办内容"输入框输入"买牛奶"
    - expect: 输入框值为"买牛奶"
  2. 点击"添加"按钮
    - expect: 列表出现 listitem，含文本"买牛奶"
    - expect: 计数显示"共 1 项，未完成 1"

#### 1.2 should-reject-empty-input

**File:** `tests/adding/should-reject-empty-input.spec.ts`

**Steps:**
  1. 输入框留空，直接点击"添加"按钮
    - expect: alert 元素可见，文本"请输入内容"
    - expect: 列表仍为空（"暂无待办"可见）

#### 1.3 should-reject-over-length-input

**File:** `tests/adding/should-reject-over-length-input.spec.ts`

**Steps:**
  1. 输入 201 个字符
  2. 点击"添加"按钮
    - expect: alert 元素可见，文本"内容不能超过 200 字"

### 2. 勾选与过滤

**Seed:** `tests/seed.spec.ts`

#### 2.1 should-toggle-and-filter-done

**File:** `tests/filtering/should-toggle-and-filter-done.spec.ts`

**Steps:**
  1. 添加"买牛奶"
  2. 勾选"完成：买牛奶"复选框
    - expect: 计数显示"共 1 项，未完成 0"
  3. 点击"已完成"过滤链接
    - expect: URL hash 为 #done
    - expect: 列表仍显示"买牛奶"（已完成的项）

#### 2.2 should-filter-active

**File:** `tests/filtering/should-filter-active.spec.ts`

**Steps:**
  1. 添加"任务A"、"任务B"
  2. 勾选"完成：任务A"
  3. 点击"未完成"过滤链接
    - expect: URL hash 为 #active
    - expect: 列表只显示"任务B"，不显示"任务A"

### 3. 删除与空态

**Seed:** `tests/seed.spec.ts`

#### 3.1 should-delete-and-show-empty

**File:** `tests/deleting/should-delete-and-show-empty.spec.ts`

**Steps:**
  1. 添加"买牛奶"
  2. 点击"删除：买牛奶"按钮
    - expect: "暂无待办"空态可见
    - expect: 计数显示"共 0 项，未完成 0"

### 4. 持久化（真实 API 往返）

**Seed:** `tests/seed.spec.ts`

#### 4.1 should-persist-after-reload

**File:** `tests/persistence/should-persist-after-reload.spec.ts`

**Steps:**
  1. 添加"买牛奶"、"记笔记"
  2. 重新加载页面
    - expect: 列表仍显示"买牛奶"与"记笔记"（数据来自真实 API，非前端缓存）

### 5. 导航

**Seed:** `tests/seed.spec.ts`

#### 5.1 should-switch-filter-by-hash

**File:** `tests/navigation/should-switch-filter-by-hash.spec.ts`

**Steps:**
  1. 点击"未完成"过滤链接
    - expect: URL hash 为 #active
    - expect: "未完成"链接处于激活态
  2. 直接导航到 /#done
    - expect: "已完成"链接处于激活态

### 6. 边界值

**Seed:** `tests/seed.spec.ts`

#### 6.1 should-handle-special-chars

**File:** `tests/edge/should-handle-special-chars.spec.ts`

**Steps:**
  1. 添加文本 `<b>bold</b> & "quotes" <script>alert(1)</script>`
    - expect: listitem 的 title 属性含完整原文（textContent 渲染，未被当作 HTML 执行）
