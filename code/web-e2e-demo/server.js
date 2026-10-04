// 极简 demo：零依赖静态文件 + 内存 Todo API（真实后端，供禁 mock E2E 测试）
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3456;
const PUBLIC_DIR = path.join(__dirname, 'public');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };

// 内存数据源：server 进程存活期间保持，刷新页面数据仍在（真实 API 往返，可测持久化）
let todos = [];
let nextId = 1;

function sendJson(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', (c) => { raw += c; });
    req.on('end', () => {
      if (!raw) return resolve({});
      try { resolve(JSON.parse(raw)); } catch (e) { reject(e); }
    });
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const apiMatch = url.pathname.match(/^\/api\/todos(?:\/(\d+))?$/);

  try {
    if (url.pathname === '/api/todos' && req.method === 'GET') {
      return sendJson(res, 200, todos);
    }
    if (url.pathname === '/api/todos' && req.method === 'POST') {
      const body = await readBody(req);
      const text = (body.text || '').trim();
      if (!text) return sendJson(res, 400, { error: '请输入内容' });
      if (text.length > 200) return sendJson(res, 400, { error: '内容不能超过 200 字' });
      const todo = { id: nextId++, text, done: false };
      todos.push(todo);
      return sendJson(res, 201, todo);
    }
    if (apiMatch && req.method === 'PATCH') {
      const todo = todos.find((t) => t.id === Number(apiMatch[1]));
      if (!todo) return sendJson(res, 404, { error: 'not found' });
      const body = await readBody(req);
      if (typeof body.done === 'boolean') todo.done = body.done;
      return sendJson(res, 200, todo);
    }
    if (apiMatch && req.method === 'DELETE') {
      const before = todos.length;
      todos = todos.filter((t) => t.id !== Number(apiMatch[1]));
      if (todos.length === before) return sendJson(res, 404, { error: 'not found' });
      return sendJson(res, 204);
    }

    // 静态文件
    const rel = url.pathname === '/' ? '/index.html' : url.pathname;
    const file = path.join(PUBLIC_DIR, path.normalize(rel).replace(/^(\.\.[/\\])+/, ''));
    if (!file.startsWith(PUBLIC_DIR)) return sendJson(res, 403, { error: 'forbidden' });
    fs.readFile(file, (err, buf) => {
      if (err) { res.writeHead(404); return res.end('Not Found'); }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream' });
      res.end(buf);
    });
  } catch (e) {
    console.error('[server] error:', e.message);
    sendJson(res, 500, { error: 'internal error' });
  }
});

server.listen(PORT, () => console.log(`demo server listening on http://localhost:${PORT}`));
