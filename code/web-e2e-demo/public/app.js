// 待办清单前端：真实 fetch 调用 /api/todos（无任何 mock）
const listEl = document.getElementById('todo-list');
const emptyEl = document.getElementById('empty');
const counterEl = document.getElementById('counter');
const errorEl = document.getElementById('error');
const form = document.getElementById('add-form');
const input = document.getElementById('todo-input');

let todos = [];
let filter = 'all';

async function api(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || `HTTP ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

async function loadTodos() {
  todos = await api('GET', '/api/todos');
  render();
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.hidden = false;
}

function clearError() {
  errorEl.textContent = '';
  errorEl.hidden = true;
}

function render() {
  const visible = todos.filter((t) =>
    filter === 'all' || (filter === 'active' ? !t.done : t.done)
  );
  listEl.innerHTML = '';
  for (const t of visible) {
    const li = document.createElement('li');
    li.className = t.done ? 'done' : '';
    li.dataset.id = t.id;

    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = t.done;
    cb.setAttribute('aria-label', `完成：${t.text}`);
    cb.addEventListener('change', async () => {
      await api('PATCH', `/api/todos/${t.id}`, { done: cb.checked });
      await loadTodos();
    });

    const span = document.createElement('span');
    span.textContent = t.text; // textContent 渲染，特殊字符天然安全
    span.title = t.text;

    const del = document.createElement('button');
    del.textContent = '删除';
    del.setAttribute('aria-label', `删除：${t.text}`);
    del.addEventListener('click', async () => {
      await api('DELETE', `/api/todos/${t.id}`);
      await loadTodos();
    });

    li.append(cb, span, del);
    listEl.appendChild(li);
  }
  emptyEl.hidden = visible.length > 0;
  const undone = todos.filter((t) => !t.done).length;
  counterEl.textContent = `共 ${todos.length} 项，未完成 ${undone}`;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) { showError('请输入内容'); return; }
  clearError();
  try {
    await api('POST', '/api/todos', { text });
    input.value = '';
    await loadTodos();
  } catch (err) {
    showError(err.message);
  }
});

function applyFilterFromHash() {
  const h = location.hash.replace('#', '');
  filter = ['all', 'active', 'done'].includes(h) ? h : 'all';
  document.querySelectorAll('#filters a').forEach((a) => {
    a.classList.toggle('active', a.dataset.filter === filter);
  });
  render();
}

window.addEventListener('hashchange', applyFilterFromHash);
applyFilterFromHash();
loadTodos().catch((e) => showError(`加载失败：${e.message}`));
